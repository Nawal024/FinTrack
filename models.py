import json
import os
from datetime import datetime

class ExpenseManager:
    @staticmethod
    def get_all_expenses():
        """Retrieve all expenses from the JSON file"""
        try:
            with open('data/expenses.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def add_expense(category, amount, date, description=""):
        """Add a new expense to the JSON file"""
        expenses = ExpenseManager.get_all_expenses()
        
        # Create new expense with a unique ID
        new_id = 1
        if expenses:
            new_id = max(int(expense['id']) for expense in expenses) + 1
            
        new_expense = {
            'id': str(new_id),
            'category': category,
            'amount': float(amount),
            'date': date,
            'description': description,
            'created_at': datetime.now().isoformat()
        }
        
        expenses.append(new_expense)
        
        with open('data/expenses.json', 'w', encoding='utf-8') as file:
            json.dump(expenses, file, ensure_ascii=False, indent=4)
            
        return new_expense

    @staticmethod
    def update_expense(expense_id, category, amount, date, description=""):
        """Update an existing expense in the JSON file"""
        expenses = ExpenseManager.get_all_expenses()
        
        for i, expense in enumerate(expenses):
            if expense['id'] == expense_id:
                expenses[i]['category'] = category
                expenses[i]['amount'] = float(amount)
                expenses[i]['date'] = date
                expenses[i]['description'] = description
                
                with open('data/expenses.json', 'w', encoding='utf-8') as file:
                    json.dump(expenses, file, ensure_ascii=False, indent=4)
                
                return expenses[i]
                
        return None

    @staticmethod
    def delete_expense(expense_id):
        """Delete an expense from the JSON file"""
        expenses = ExpenseManager.get_all_expenses()
        
        for i, expense in enumerate(expenses):
            if expense['id'] == expense_id:
                deleted_expense = expenses.pop(i)
                
                with open('data/expenses.json', 'w', encoding='utf-8') as file:
                    json.dump(expenses, file, ensure_ascii=False, indent=4)
                
                return deleted_expense
                
        return None

    @staticmethod
    def get_expense_by_id(expense_id):
        """Retrieve a specific expense by ID"""
        expenses = ExpenseManager.get_all_expenses()
        
        for expense in expenses:
            if expense['id'] == expense_id:
                return expense
                
        return None

    @staticmethod
    def get_expenses_by_category(category):
        """Get all expenses for a specific category"""
        expenses = ExpenseManager.get_all_expenses()
        return [expense for expense in expenses if expense['category'] == category]

    @staticmethod
    def get_expenses_by_date_range(start_date, end_date):
        """Get all expenses within a date range"""
        expenses = ExpenseManager.get_all_expenses()
        
        # Convert string dates to datetime objects for comparison
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        return [
            expense for expense in expenses 
            if start <= datetime.strptime(expense['date'], '%Y-%m-%d') <= end
        ]

    @staticmethod
    def get_category_totals():
        """Get total expenses by category"""
        expenses = ExpenseManager.get_all_expenses()
        
        category_totals = {}
        for expense in expenses:
            category = expense['category']
            amount = expense['amount']
            
            if category in category_totals:
                category_totals[category] += amount
            else:
                category_totals[category] = amount
                
        return category_totals

    @staticmethod
    def get_monthly_totals():
        """Get total expenses by month"""
        expenses = ExpenseManager.get_all_expenses()
        
        monthly_totals = {}
        for expense in expenses:
            date_obj = datetime.strptime(expense['date'], '%Y-%m-%d')
            month_key = f"{date_obj.year}-{date_obj.month:02d}"
            amount = expense['amount']
            
            if month_key in monthly_totals:
                monthly_totals[month_key] += amount
            else:
                monthly_totals[month_key] = amount
                
        return monthly_totals

class CategoryManager:
    @staticmethod
    def get_all_categories():
        """Retrieve all expense categories"""
        try:
            with open('data/categories.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def add_category(name_en, name_ar, budget=0):
        """Add a new expense category"""
        categories = CategoryManager.get_all_categories()
        
        # Create new category with a unique ID
        new_id = 1
        if categories:
            new_id = max(int(category['id']) for category in categories) + 1
            
        new_category = {
            'id': str(new_id),
            'name_en': name_en,
            'name_ar': name_ar,
            'budget': float(budget)
        }
        
        categories.append(new_category)
        
        with open('data/categories.json', 'w', encoding='utf-8') as file:
            json.dump(categories, file, ensure_ascii=False, indent=4)
            
        return new_category

    @staticmethod
    def update_category(category_id, name_en, name_ar, budget):
        """Update an existing category"""
        categories = CategoryManager.get_all_categories()
        
        for i, category in enumerate(categories):
            if category['id'] == category_id:
                categories[i]['name_en'] = name_en
                categories[i]['name_ar'] = name_ar
                categories[i]['budget'] = float(budget)
                
                with open('data/categories.json', 'w', encoding='utf-8') as file:
                    json.dump(categories, file, ensure_ascii=False, indent=4)
                
                return categories[i]
                
        return None

    @staticmethod
    def get_category_by_id(category_id):
        """Get a category by its ID"""
        categories = CategoryManager.get_all_categories()
        
        for category in categories:
            if category['id'] == category_id:
                return category
                
        return None

    @staticmethod
    def get_category_budget(category_id):
        """Get the budget for a specific category"""
        category = CategoryManager.get_category_by_id(category_id)
        
        if category:
            return category['budget']
            
        return 0
