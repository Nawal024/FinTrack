import json
import os
from datetime import datetime
from app import db
from sqlalchemy import func, and_, desc
from sqlalchemy.exc import SQLAlchemyError
import logging
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Define User model for authentication
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    expenses = db.relationship('Expense', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Define SQLAlchemy models for database tables
class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'category': self.category,
            'amount': float(self.amount),
            'date': self.date.strftime('%Y-%m-%d'),
            'description': self.description or '',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_id': self.user_id
        }

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_en = db.Column(db.String(100), nullable=False)
    name_ar = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': str(self.id),
            'name_en': self.name_en,
            'name_ar': self.name_ar,
            'budget': float(self.budget),
            'user_id': self.user_id
        }

# Maintain the original interface for backward compatibility
class ExpenseManager:
    @staticmethod
    def get_all_expenses(user_id=None):
        """Retrieve all expenses from the database for a specific user"""
        try:
            if user_id:
                expenses = Expense.query.filter_by(user_id=user_id).order_by(desc(Expense.date)).all()
            else:
                expenses = Expense.query.order_by(desc(Expense.date)).all()
            return [expense.to_dict() for expense in expenses]
        except SQLAlchemyError as e:
            logging.error(f"Database error retrieving expenses: {str(e)}")
            return []

    @staticmethod
    def add_expense(category, amount, date, description="", user_id=None):
        """Add a new expense to the database"""
        try:
            # Convert date string to date object if it's a string
            if isinstance(date, str):
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            else:
                date_obj = date
            
            # Create new expense
            new_expense = Expense(
                category=category,
                amount=float(amount),
                date=date_obj,
                description=description,
                user_id=user_id
            )
            
            # Add and commit
            db.session.add(new_expense)
            db.session.commit()
            
            return new_expense.to_dict()
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding expense: {str(e)}")
            return None

    @staticmethod
    def update_expense(expense_id, category, amount, date, description="", user_id=None):
        """Update an existing expense in the database"""
        try:
            # Find expense by ID and optionally user_id
            if user_id:
                expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
            else:
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
    def delete_expense(expense_id, user_id=None):
        """Delete an expense from the database"""
        try:
            # Find expense by ID and optionally user_id
            if user_id:
                expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
            else:
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
    def get_expense_by_id(expense_id, user_id=None):
        """Retrieve a specific expense by ID from the database"""
        try:
            if user_id:
                expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
            else:
                expense = Expense.query.get(expense_id)
            return expense.to_dict() if expense else None
        except Exception as e:
            logging.error(f"Error retrieving expense by ID: {str(e)}")
            return None

    @staticmethod
    def get_expenses_by_category(category, user_id=None):
        """Get all expenses for a specific category from the database"""
        try:
            if user_id:
                expenses = Expense.query.filter_by(category=category, user_id=user_id).all()
            else:
                expenses = Expense.query.filter_by(category=category).all()
            return [expense.to_dict() for expense in expenses]
        except Exception as e:
            logging.error(f"Error retrieving expenses by category: {str(e)}")
            return []

    @staticmethod
    def get_expenses_by_date_range(start_date, end_date, user_id=None):
        """Get all expenses within a date range from the database"""
        try:
            # Convert string dates to date objects
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Query database with date range and optional user_id
            query = Expense.query.filter(
                and_(
                    Expense.date >= start,
                    Expense.date <= end
                )
            )
            
            # Add user filter if provided
            if user_id:
                query = query.filter_by(user_id=user_id)
                
            expenses = query.all()
            
            return [expense.to_dict() for expense in expenses]
        except Exception as e:
            logging.error(f"Error retrieving expenses by date range: {str(e)}")
            return []

    @staticmethod
    def get_category_totals(user_id=None):
        """Get total expenses by category from the database"""
        try:
            # Use SQLAlchemy aggregate functions
            query = db.session.query(
                Expense.category,
                func.sum(Expense.amount).label('total')
            )
            
            # Filter by user if provided
            if user_id:
                query = query.filter_by(user_id=user_id)
                
            category_totals = query.group_by(Expense.category).all()
            
            # Convert to dictionary
            return {category: float(total) for category, total in category_totals}
        except Exception as e:
            logging.error(f"Error retrieving category totals: {str(e)}")
            return {}

    @staticmethod
    def get_monthly_totals(user_id=None):
        """Get total expenses by month from the database"""
        try:
            # Extract year and month from date and group
            query = db.session.query(
                func.extract('year', Expense.date).label('year'),
                func.extract('month', Expense.date).label('month'),
                func.sum(Expense.amount).label('total')
            )
            
            # Filter by user if provided
            if user_id:
                query = query.filter_by(user_id=user_id)
                
            monthly_totals_query = query.group_by(
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
    def get_all_categories(user_id=None):
        """Retrieve all expense categories from the database"""
        try:
            if user_id:
                categories = Category.query.all()
            else:
                categories = Category.query.all()
            return [category.to_dict() for category in categories]
        except Exception as e:
            logging.error(f"Error retrieving categories: {str(e)}")
            return []

    @staticmethod
    def add_category(name_en, name_ar, budget=0, user_id=None):
        """Add a new expense category to the database"""
        try:
            # Create new category
            new_category = Category(
                name_en=name_en,
                name_ar=name_ar,
                budget=float(budget),
                user_id=user_id
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
    def update_category(category_id, name_en, name_ar, budget, user_id=None):
        """Update an existing category in the database"""
        try:
            # Find category by ID and optionally user_id
            if user_id:
                category = Category.query.filter_by(id=category_id, user_id=user_id).first()
            else:
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
    def get_category_by_id(category_id, user_id=None):
        """Get a category by its ID from the database"""
        try:
            if user_id:
                category = Category.query.filter_by(id=category_id, user_id=user_id).first()
            else:
                category = Category.query.get(category_id)
            return category.to_dict() if category else None
        except Exception as e:
            logging.error(f"Error retrieving category by ID: {str(e)}")
            return None

    @staticmethod
    def get_category_budget(category_id, user_id=None):
        """Get the budget for a specific category from the database"""
        try:
            if user_id:
                category = Category.query.filter_by(id=category_id, user_id=user_id).first()
            else:
                category = Category.query.get(category_id)
            return float(category.budget) if category else 0
        except Exception as e:
            logging.error(f"Error retrieving category budget: {str(e)}")
            return 0

# Function to migrate data from JSON files to database if needed
def migrate_data_from_json_to_db():
    """Migrate existing data from JSON files to database"""
    try:
        # Check if a default user exists; if not, create one
        default_user = User.query.filter_by(username='default_user').first()
        if not default_user:
            default_user = User(
                username='default_user',
                email='default@example.com'
            )
            default_user.set_password('default_password')
            db.session.add(default_user)
            db.session.commit()
            logging.info("Created default user for data migration")
        
        # Check if there are any categories without user_id
        categories_without_user = db.session.query(Category).filter(Category.user_id.is_(None)).all()
        if categories_without_user:
            for category in categories_without_user:
                category.user_id = default_user.id
            db.session.commit()
            logging.info(f"Assigned {len(categories_without_user)} categories to default user")
        
        # Check if there are any expenses without user_id
        expenses_without_user = db.session.query(Expense).filter(Expense.user_id.is_(None)).all()
        if expenses_without_user:
            for expense in expenses_without_user:
                expense.user_id = default_user.id
            db.session.commit()
            logging.info(f"Assigned {len(expenses_without_user)} expenses to default user")
        
        # If there are no expenses or categories at all, create from JSON
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
                            budget=float(category_data['budget']),
                            user_id=default_user.id
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
                            category=expense_data['category'],
                            amount=float(expense_data['amount']),
                            date=date_obj,
                            description=expense_data.get('description', ''),
                            created_at=created_at,
                            user_id=default_user.id
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
                
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in migrate_data_from_json_to_db: {str(e)}")
