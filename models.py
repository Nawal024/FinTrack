import json
import os
from datetime import datetime
from app import db
from sqlalchemy import func, and_, desc
from sqlalchemy.exc import SQLAlchemyError
import logging

# Define SQLAlchemy models for database tables
class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': str(self.id),
            'category': self.category,
            'amount': float(self.amount),
            'date': self.date.strftime('%Y-%m-%d'),
            'description': self.description or '',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(100), nullable=False)
    name_ar = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.Float, default=0.0)
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': str(self.id),
            'name_en': self.name_en,
            'name_ar': self.name_ar,
            'budget': float(self.budget)
        }

# Maintain the original interface for backward compatibility
class ExpenseManager:
    @staticmethod
    def get_all_expenses():
        """Retrieve all expenses from the database"""
        try:
            expenses = Expense.query.order_by(desc(Expense.date)).all()
            return [expense.to_dict() for expense in expenses]
        except SQLAlchemyError as e:
            logging.error(f"Database error retrieving expenses: {str(e)}")
            return []

    @staticmethod
    def add_expense(category, amount, date, description=""):
        """Add a new expense to the database"""
        try:
            # Convert date string to date object
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            
            # Create new expense
            new_expense = Expense(
                category=category,
                amount=float(amount),
                date=date_obj,
                description=description,
                created_at=datetime.now()
            )
            
            # Add to database
            db.session.add(new_expense)
            db.session.commit()
            
            return new_expense.to_dict()
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding expense: {str(e)}")
            return None

    @staticmethod
    def update_expense(expense_id, category, amount, date, description=""):
        """Update an existing expense in the database"""
        try:
            # Find expense by ID
            expense = Expense.query.get(expense_id)
            
            if expense:
                # Update fields
                expense.category = category
                expense.amount = float(amount)
                expense.date = datetime.strptime(date, '%Y-%m-%d').date()
                expense.description = description
                
                # Commit changes
                db.session.commit()
                
                return expense.to_dict()
            return None
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating expense: {str(e)}")
            return None

    @staticmethod
    def delete_expense(expense_id):
        """Delete an expense from the database"""
        try:
            # Find expense by ID
            expense = Expense.query.get(expense_id)
            
            if expense:
                # Store the data for return value
                expense_data = expense.to_dict()
                
                # Delete the expense
                db.session.delete(expense)
                db.session.commit()
                
                return expense_data
            return None
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error deleting expense: {str(e)}")
            return None

    @staticmethod
    def get_expense_by_id(expense_id):
        """Retrieve a specific expense by ID from the database"""
        try:
            expense = Expense.query.get(expense_id)
            return expense.to_dict() if expense else None
        except Exception as e:
            logging.error(f"Error retrieving expense by ID: {str(e)}")
            return None

    @staticmethod
    def get_expenses_by_category(category):
        """Get all expenses for a specific category from the database"""
        try:
            expenses = Expense.query.filter_by(category=category).all()
            return [expense.to_dict() for expense in expenses]
        except Exception as e:
            logging.error(f"Error retrieving expenses by category: {str(e)}")
            return []

    @staticmethod
    def get_expenses_by_date_range(start_date, end_date):
        """Get all expenses within a date range from the database"""
        try:
            # Convert string dates to date objects
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Query database with date range
            expenses = Expense.query.filter(
                and_(
                    Expense.date >= start,
                    Expense.date <= end
                )
            ).all()
            
            return [expense.to_dict() for expense in expenses]
        except Exception as e:
            logging.error(f"Error retrieving expenses by date range: {str(e)}")
            return []

    @staticmethod
    def get_category_totals():
        """Get total expenses by category from the database"""
        try:
            # Use SQLAlchemy aggregate functions
            category_totals = db.session.query(
                Expense.category,
                func.sum(Expense.amount).label('total')
            ).group_by(Expense.category).all()
            
            # Convert to dictionary
            return {category: float(total) for category, total in category_totals}
        except Exception as e:
            logging.error(f"Error retrieving category totals: {str(e)}")
            return {}

    @staticmethod
    def get_monthly_totals():
        """Get total expenses by month from the database"""
        try:
            # Extract year and month from date and group
            monthly_totals_query = db.session.query(
                func.extract('year', Expense.date).label('year'),
                func.extract('month', Expense.date).label('month'),
                func.sum(Expense.amount).label('total')
            ).group_by(
                func.extract('year', Expense.date),
                func.extract('month', Expense.date)
            ).all()
            
            # Format the result as required
            monthly_totals = {}
            for year, month, total in monthly_totals_query:
                month_key = f"{int(year)}-{int(month):02d}"
                monthly_totals[month_key] = float(total)
                
            return monthly_totals
        except Exception as e:
            logging.error(f"Error retrieving monthly totals: {str(e)}")
            return {}

class CategoryManager:
    @staticmethod
    def get_all_categories():
        """Retrieve all expense categories from the database"""
        try:
            categories = Category.query.all()
            return [category.to_dict() for category in categories]
        except Exception as e:
            logging.error(f"Error retrieving categories: {str(e)}")
            return []

    @staticmethod
    def add_category(name_en, name_ar, budget=0):
        """Add a new expense category to the database"""
        try:
            # Create new category
            new_category = Category(
                name_en=name_en,
                name_ar=name_ar,
                budget=float(budget)
            )
            
            # Add to database
            db.session.add(new_category)
            db.session.commit()
            
            return new_category.to_dict()
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding category: {str(e)}")
            return None

    @staticmethod
    def update_category(category_id, name_en, name_ar, budget):
        """Update an existing category in the database"""
        try:
            # Find category by ID
            category = Category.query.get(category_id)
            
            if category:
                # Update fields
                category.name_en = name_en
                category.name_ar = name_ar
                category.budget = float(budget)
                
                # Commit changes
                db.session.commit()
                
                return category.to_dict()
            return None
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating category: {str(e)}")
            return None

    @staticmethod
    def get_category_by_id(category_id):
        """Get a category by its ID from the database"""
        try:
            category = Category.query.get(category_id)
            return category.to_dict() if category else None
        except Exception as e:
            logging.error(f"Error retrieving category by ID: {str(e)}")
            return None

    @staticmethod
    def get_category_budget(category_id):
        """Get the budget for a specific category from the database"""
        try:
            category = Category.query.get(category_id)
            return float(category.budget) if category else 0
        except Exception as e:
            logging.error(f"Error retrieving category budget: {str(e)}")
            return 0

# Function to migrate data from JSON files to database if needed
def migrate_data_from_json_to_db():
    """Migrate existing data from JSON files to database"""
    # Check if migration is needed (if database tables are empty)
    if Expense.query.count() == 0 and Category.query.count() == 0:
        try:
            # Migrate categories
            try:
                with open('data/categories.json', 'r', encoding='utf-8') as file:
                    categories = json.load(file)
                    
                for category_data in categories:
                    new_category = Category(
                        id=int(category_data['id']),
                        name_en=category_data['name_en'],
                        name_ar=category_data['name_ar'],
                        budget=float(category_data['budget'])
                    )
                    db.session.add(new_category)
            except (FileNotFoundError, json.JSONDecodeError):
                pass
                
            # Migrate expenses
            try:
                with open('data/expenses.json', 'r', encoding='utf-8') as file:
                    expenses = json.load(file)
                    
                for expense_data in expenses:
                    # Convert string date to date object
                    date_obj = datetime.strptime(expense_data['date'], '%Y-%m-%d').date()
                    created_at = datetime.fromisoformat(expense_data['created_at']) if 'created_at' in expense_data else datetime.now()
                    
                    new_expense = Expense(
                        id=int(expense_data['id']),
                        category=expense_data['category'],
                        amount=float(expense_data['amount']),
                        date=date_obj,
                        description=expense_data.get('description', ''),
                        created_at=created_at
                    )
                    db.session.add(new_expense)
            except (FileNotFoundError, json.JSONDecodeError):
                pass
                
            # Commit all changes
            db.session.commit()
            logging.info("Data migration from JSON to database completed successfully")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error migrating data from JSON to database: {str(e)}")
