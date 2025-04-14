from flask import render_template, request, redirect, url_for, jsonify, flash, session
from app import app
from models import ExpenseManager, CategoryManager
from utils import get_insights, get_spending_alerts, get_savings_tips
from datetime import datetime, timedelta
import json

# Dictionary for category name translations
category_translations = {
    'Food': 'طعام',
    'Transport': 'نقل',
    'Shopping': 'تسوق',
    'Bills': 'فواتير',
    'Entertainment': 'ترفيه',
    'Health': 'صحة',
    'Education': 'تعليم',
    'Other': 'أخرى'
}

# Set Arabic as the only language
@app.before_request
def set_language():
    session['lang'] = 'ar'  # Always use Arabic

# Helper function to get category display name in Arabic
def get_category_display_name(category_name_en):
    return category_translations.get(category_name_en, category_name_en)

@app.route('/')
def index():
    # Get current month's expenses
    today = datetime.now()
    start_of_month = datetime(today.year, today.month, 1).strftime('%Y-%m-%d')
    end_of_month = (datetime(today.year, today.month + 1, 1) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    monthly_expenses = ExpenseManager.get_expenses_by_date_range(start_of_month, end_of_month)
    total_spent = sum(expense['amount'] for expense in monthly_expenses)
    
    # Get categories for the form
    categories = CategoryManager.get_all_categories()
    
    # Get spending alerts and savings tips
    alerts = get_spending_alerts()
    tips = get_savings_tips()
    
    # Get category totals for pie chart with localized category names
    category_totals = {}
    display_category_totals = {}
    # Dictionary to keep track of English category names for each Arabic category name
    category_mappings = {}
    
    for expense in monthly_expenses:
        category_en = expense['category']
        
        # Add to English category totals (for backend operations)
        if category_en in category_totals:
            category_totals[category_en] += expense['amount']
        else:
            category_totals[category_en] = expense['amount']
            
        # Add to display category totals (for frontend display)
        category_display = get_category_display_name(category_en)
        if category_display in display_category_totals:
            display_category_totals[category_display] += expense['amount']
        else:
            display_category_totals[category_display] = expense['amount']
            
        # Store mapping from Arabic to English
        category_mappings[category_display] = category_en
    
    return render_template(
        'index.html',
        categories=categories,
        total_spent=total_spent,
        category_totals=json.dumps(display_category_totals),
        category_names=json.dumps(category_mappings),
        alerts=alerts,
        tips=tips
    )

@app.route('/expenses')
def expenses():
    # Get all expenses, sorted by date (newest first)
    all_expenses = ExpenseManager.get_all_expenses()
    all_expenses.sort(key=lambda x: x['date'], reverse=True)
    
    # Add display category name for each expense
    for expense in all_expenses:
        expense['display_category'] = get_category_display_name(expense['category'])
    
    # Get categories for the form
    categories = CategoryManager.get_all_categories()
    
    return render_template(
        'expenses.html',
        expenses=all_expenses,
        categories=categories,
        translations=category_translations
    )

@app.route('/budget')
def budget():
    # Get all categories with their budgets
    categories = CategoryManager.get_all_categories()
    
    # Get current month spending for each category
    today = datetime.now()
    start_of_month = datetime(today.year, today.month, 1).strftime('%Y-%m-%d')
    end_of_month = (datetime(today.year, today.month + 1, 1) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    monthly_expenses = ExpenseManager.get_expenses_by_date_range(start_of_month, end_of_month)
    
    # Calculate spending per category
    category_spending = {}
    for expense in monthly_expenses:
        category = expense['category']
        if category in category_spending:
            category_spending[category] += expense['amount']
        else:
            category_spending[category] = expense['amount']
    
    # Add spending to each category
    for category in categories:
        category_id = category['id']
        category_name = category['name_en']
        
        # Always use Arabic display name
        category['display_name'] = category['name_ar']
        
        if category_name in category_spending:
            category['spent'] = category_spending[category_name]
        else:
            category['spent'] = 0
            
        # Calculate percentage of budget spent
        if category['budget'] > 0:
            category['percentage'] = (category['spent'] / category['budget']) * 100
        else:
            category['percentage'] = 0
    
    return render_template('budget.html', categories=categories)

@app.route('/insights')
def insights():
    # Get insights data
    insights_data = get_insights()
    
    # Get monthly expenses for chart
    monthly_totals = ExpenseManager.get_monthly_totals()
    
    # Sort months chronologically
    sorted_months = sorted(monthly_totals.keys())
    
    # Prepare data for chart
    chart_labels = sorted_months
    chart_values = [monthly_totals[month] for month in sorted_months]
    
    return render_template(
        'insights.html',
        insights=insights_data,
        chart_labels=json.dumps(chart_labels),
        chart_values=json.dumps(chart_values)
    )

# API endpoints for AJAX operations
@app.route('/api/expenses', methods=['POST'])
def add_expense_api():
    # Get form data
    category = request.form.get('category')
    amount = request.form.get('amount')
    date = request.form.get('date')
    description = request.form.get('description', '')
    
    if not all([category, amount, date]):
        return jsonify({'success': False, 'message': 'جميع الحقول مطلوبة'}), 400
    
    try:
        new_expense = ExpenseManager.add_expense(category, amount, date, description)
        return jsonify({'success': True, 'expense': new_expense})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/expenses/<expense_id>', methods=['PUT'])
def update_expense_api(expense_id):
    # Get form data
    data = request.get_json()
    
    category = data.get('category')
    amount = data.get('amount')
    date = data.get('date')
    description = data.get('description', '')
    
    if not all([category, amount, date]):
        return jsonify({'success': False, 'message': 'جميع الحقول مطلوبة'}), 400
    
    try:
        updated_expense = ExpenseManager.update_expense(expense_id, category, amount, date, description)
        if updated_expense:
            return jsonify({'success': True, 'expense': updated_expense})
        else:
            return jsonify({'success': False, 'message': 'المصروف غير موجود'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/expenses/<expense_id>', methods=['DELETE'])
def delete_expense_api(expense_id):
    try:
        deleted_expense = ExpenseManager.delete_expense(expense_id)
        if deleted_expense:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'المصروف غير موجود'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/categories', methods=['POST'])
def add_category_api():
    # Get form data
    name_en = request.form.get('name_en')
    name_ar = request.form.get('name_ar')
    budget = request.form.get('budget', 0)
    
    if not all([name_en, name_ar]):
        return jsonify({'success': False, 'message': 'اسم الفئة مطلوب'}), 400
    
    try:
        new_category = CategoryManager.add_category(name_en, name_ar, budget)
        return jsonify({'success': True, 'category': new_category})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/categories/<category_id>', methods=['PUT'])
def update_category_api(category_id):
    # Get form data
    data = request.get_json()
    
    name_en = data.get('name_en')
    name_ar = data.get('name_ar')
    budget = data.get('budget', 0)
    
    if not all([name_en, name_ar]):
        return jsonify({'success': False, 'message': 'اسم الفئة مطلوب'}), 400
    
    try:
        updated_category = CategoryManager.update_category(category_id, name_en, name_ar, budget)
        if updated_category:
            return jsonify({'success': True, 'category': updated_category})
        else:
            return jsonify({'success': False, 'message': 'الفئة غير موجودة'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
