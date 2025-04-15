from flask import render_template, request, redirect, url_for, jsonify, flash, session
from app import app, db
from models import ExpenseManager, CategoryManager, User
from utils import get_insights, get_spending_alerts, get_savings_tips
from datetime import datetime, timedelta
import json
from forms import LoginForm, RegistrationForm
from flask_login import login_user, logout_user, current_user, login_required

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

# Authentication routes
@app.route('/login/google')
def google_login():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": app.config['GOOGLE_CLIENT_ID'],
                "client_secret": app.config['GOOGLE_CLIENT_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=['openid', 'email', 'profile']
    )
    
    flow.redirect_uri = url_for('google_callback', _external=True)
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    session['state'] = state
    return redirect(authorization_url)

@app.route('/login/google/callback')
def google_callback():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": app.config['GOOGLE_CLIENT_ID'],
                "client_secret": app.config['GOOGLE_CLIENT_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=['openid', 'email', 'profile']
    )
    
    flow.redirect_uri = url_for('google_callback', _external=True)
    flow.fetch_token(authorization_response=request.url)
    
    credentials = flow.credentials
    response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo',
                          headers={'Authorization': f'Bearer {credentials.token}'})
    user_info = response.json()
    
    # Check if user exists, if not create new user
    user = User.query.filter_by(email=user_info['email']).first()
    if not user:
        user = User(
            username=user_info['email'].split('@')[0],
            email=user_info['email']
        )
        user.set_password(os.urandom(24).hex())  # Random password for Google users
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
            return redirect(url_for('login'))
            
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('index')
            
        flash('تم تسجيل الدخول بنجاح', 'success')
        return redirect(next_page)
        
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Create default categories for new user
        from utils import create_default_categories_for_user
        create_default_categories_for_user(user.id)
        
        flash('تم تسجيل الحساب بنجاح! يمكنك الآن تسجيل الدخول', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'info')
    return redirect(url_for('index'))

# Helper function to get category display name in Arabic
def get_category_display_name(category_name_en):
    return category_translations.get(category_name_en, category_name_en)

@app.route('/')
def index():
    # Check if user is not authenticated
    if not current_user.is_authenticated:
        # Show welcome page for anonymous users
        return render_template('index.html', 
                              categories=[], 
                              total_spent=0, 
                              category_totals=json.dumps({}),
                              category_names=json.dumps({}),
                              alerts=[],
                              tips=[],
                              show_welcome=True)
    
    # User is authenticated, get data for current user
    user_id = current_user.id
    
    # Get current month's expenses
    today = datetime.now()
    start_of_month = datetime(today.year, today.month, 1).strftime('%Y-%m-%d')
    end_of_month = (datetime(today.year, today.month + 1, 1) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    monthly_expenses = ExpenseManager.get_expenses_by_date_range(start_of_month, end_of_month, user_id=user_id)
    total_spent = sum(expense['amount'] for expense in monthly_expenses)
    
    # Get categories for the form
    categories = CategoryManager.get_all_categories(user_id=user_id)
    
    # Get spending alerts and savings tips for this user
    alerts = get_spending_alerts(user_id=user_id)
    tips = get_savings_tips(user_id=user_id)
    
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
        tips=tips,
        show_welcome=False
    )

@app.route('/expenses')
@login_required
def expenses():
    # Get user ID
    user_id = current_user.id
    
    # Get all expenses for this user, sorted by date (newest first)
    all_expenses = ExpenseManager.get_all_expenses(user_id=user_id)
    all_expenses.sort(key=lambda x: x['date'], reverse=True)
    
    # Add display category name for each expense
    for expense in all_expenses:
        expense['display_category'] = get_category_display_name(expense['category'])
    
    # Get categories for the form
    categories = CategoryManager.get_all_categories(user_id=user_id)
    
    return render_template(
        'expenses.html',
        expenses=all_expenses,
        categories=categories,
        translations=category_translations
    )

@app.route('/budget')
@login_required
def budget():
    # Get user ID
    user_id = current_user.id
    
    # Get all categories with their budgets for this user
    categories = CategoryManager.get_all_categories(user_id=user_id)
    
    # Get current month spending for each category
    today = datetime.now()
    start_of_month = datetime(today.year, today.month, 1).strftime('%Y-%m-%d')
    end_of_month = (datetime(today.year, today.month + 1, 1) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    monthly_expenses = ExpenseManager.get_expenses_by_date_range(start_of_month, end_of_month, user_id=user_id)
    
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
@login_required
def insights():
    # Get user ID
    user_id = current_user.id
    
    # Get insights data for this user
    insights_data = get_insights(user_id=user_id)
    
    # Get monthly expenses for chart for this user
    monthly_totals = ExpenseManager.get_monthly_totals(user_id=user_id)
    
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
@login_required
def add_expense_api():
    # Get user ID
    user_id = current_user.id
    
    # Get form data
    category = request.form.get('category')
    amount = request.form.get('amount')
    date = request.form.get('date')
    description = request.form.get('description', '')
    
    if not all([category, amount, date]):
        return jsonify({'success': False, 'message': 'جميع الحقول مطلوبة'}), 400
    
    try:
        new_expense = ExpenseManager.add_expense(category, amount, date, description, user_id=user_id)
        return jsonify({'success': True, 'expense': new_expense})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/expenses/<expense_id>', methods=['PUT'])
@login_required
def update_expense_api(expense_id):
    # Get user ID
    user_id = current_user.id
    
    # Get form data
    data = request.get_json()
    
    category = data.get('category')
    amount = data.get('amount')
    date = data.get('date')
    description = data.get('description', '')
    
    if not all([category, amount, date]):
        return jsonify({'success': False, 'message': 'جميع الحقول مطلوبة'}), 400
    
    try:
        updated_expense = ExpenseManager.update_expense(expense_id, category, amount, date, description, user_id=user_id)
        if updated_expense:
            return jsonify({'success': True, 'expense': updated_expense})
        else:
            return jsonify({'success': False, 'message': 'المصروف غير موجود'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/expenses/<expense_id>', methods=['DELETE'])
@login_required
def delete_expense_api(expense_id):
    # Get user ID
    user_id = current_user.id
    
    try:
        deleted_expense = ExpenseManager.delete_expense(expense_id, user_id=user_id)
        if deleted_expense:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'المصروف غير موجود'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/categories', methods=['POST'])
@login_required
def add_category_api():
    # Get user ID
    user_id = current_user.id
    
    # Get form data
    name_en = request.form.get('name_en')
    name_ar = request.form.get('name_ar')
    budget = request.form.get('budget', 0)
    
    if not all([name_en, name_ar]):
        return jsonify({'success': False, 'message': 'اسم الفئة مطلوب'}), 400
    
    try:
        new_category = CategoryManager.add_category(name_en, name_ar, budget, user_id=user_id)
        return jsonify({'success': True, 'category': new_category})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/categories/<category_id>', methods=['PUT'])
@login_required
def update_category_api(category_id):
    # Get user ID
    user_id = current_user.id
    
    # Get form data
    data = request.get_json()
    
    name_en = data.get('name_en')
    name_ar = data.get('name_ar')
    budget = data.get('budget', 0)
    
    if not all([name_en, name_ar]):
        return jsonify({'success': False, 'message': 'اسم الفئة مطلوب'}), 400
    
    try:
        updated_category = CategoryManager.update_category(category_id, name_en, name_ar, budget, user_id=user_id)
        if updated_category:
            return jsonify({'success': True, 'category': updated_category})
        else:
            return jsonify({'success': False, 'message': 'الفئة غير موجودة'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
