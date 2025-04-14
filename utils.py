import json
import os
from datetime import datetime, timedelta
from models import ExpenseManager, CategoryManager

def initialize_data_files():
    """Initialize data files if they don't exist (for backward compatibility)"""
    # Create expenses.json if it doesn't exist
    if not os.path.exists('data/expenses.json'):
        with open('data/expenses.json', 'w', encoding='utf-8') as file:
            json.dump([], file)
    
    # Create categories.json if it doesn't exist
    if not os.path.exists('data/categories.json'):
        default_categories = [
            {
                "id": "1",
                "name_en": "Food",
                "name_ar": "طعام",
                "budget": 1000
            },
            {
                "id": "2",
                "name_en": "Transport",
                "name_ar": "نقل",
                "budget": 500
            },
            {
                "id": "3",
                "name_en": "Shopping",
                "name_ar": "تسوق",
                "budget": 800
            },
            {
                "id": "4",
                "name_en": "Bills",
                "name_ar": "فواتير",
                "budget": 1200
            },
            {
                "id": "5",
                "name_en": "Entertainment",
                "name_ar": "ترفيه",
                "budget": 400
            }
        ]
        
        with open('data/categories.json', 'w', encoding='utf-8') as file:
            json.dump(default_categories, file, ensure_ascii=False, indent=4)

def create_default_categories_if_empty():
    """Create default categories in the database if none exist"""
    # Import here to avoid circular imports
    from app import db
    from models import Category, User
    
    # Check if there are any categories in the database
    try:
        from app import app
        with app.app_context():
            # Get or create default user
            default_user = User.query.filter_by(username='default_user').first()
            if not default_user:
                from werkzeug.security import generate_password_hash
                default_user = User(
                    username='default_user',
                    email='default@example.com',
                    password_hash=generate_password_hash('default_password')
                )
                db.session.add(default_user)
                db.session.commit()
                print("Created default user for categories")
                
            # Check if user has any categories
            if Category.query.filter_by(user_id=default_user.id).count() == 0:
                # Define default categories
                default_categories = [
                    {
                        "name_en": "Food",
                        "name_ar": "طعام",
                        "budget": 1000
                    },
                    {
                        "name_en": "Transport",
                        "name_ar": "نقل",
                        "budget": 500
                    },
                    {
                        "name_en": "Shopping",
                        "name_ar": "تسوق",
                        "budget": 800
                    },
                    {
                        "name_en": "Bills",
                        "name_ar": "فواتير",
                        "budget": 1200
                    },
                    {
                        "name_en": "Entertainment",
                        "name_ar": "ترفيه",
                        "budget": 400
                    },
                    {
                        "name_en": "Health",
                        "name_ar": "صحة",
                        "budget": 600
                    },
                    {
                        "name_en": "Education",
                        "name_ar": "تعليم",
                        "budget": 700
                    },
                    {
                        "name_en": "Other",
                        "name_ar": "أخرى",
                        "budget": 0
                    }
                ]
                
                # Add categories to database
                for cat_data in default_categories:
                    category = Category(
                        name_en=cat_data["name_en"],
                        name_ar=cat_data["name_ar"],
                        budget=cat_data["budget"],
                        user_id=default_user.id
                    )
                    db.session.add(category)
                
                # Commit to database
                db.session.commit()
                print(f"Default categories created for user {default_user.username}")
    except Exception as e:
        print(f"Error creating default categories: {str(e)}")

def get_insights():
    """Generate spending insights based on user's expenses"""
    insights = []
    
    # Get current month's expenses
    today = datetime.now()
    start_of_month = datetime(today.year, today.month, 1).strftime('%Y-%m-%d')
    end_of_month = (datetime(today.year, today.month + 1, 1) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Get previous month's date range
    first_of_prev_month = (datetime(today.year, today.month, 1) - timedelta(days=1)).replace(day=1)
    start_of_prev_month = first_of_prev_month.strftime('%Y-%m-%d')
    end_of_prev_month = (datetime(today.year, today.month, 1) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Get expenses for current and previous month
    current_expenses = ExpenseManager.get_expenses_by_date_range(start_of_month, end_of_month)
    previous_expenses = ExpenseManager.get_expenses_by_date_range(start_of_prev_month, end_of_prev_month)
    
    # Calculate totals
    current_total = sum(expense['amount'] for expense in current_expenses)
    previous_total = sum(expense['amount'] for expense in previous_expenses)
    
    # Calculate spending change percentage
    if previous_total > 0:
        change_percentage = ((current_total - previous_total) / previous_total) * 100
        if change_percentage > 10:
            insights.append({
                'type': 'warning',
                'message': f'إنفاقك هذا الشهر أعلى بنسبة {change_percentage:.1f}% من الشهر الماضي'
            })
        elif change_percentage < -10:
            insights.append({
                'type': 'success',
                'message': f'أحسنت! إنفاقك هذا الشهر أقل بنسبة {abs(change_percentage):.1f}% من الشهر الماضي'
            })
    
    # Analyze category spending
    categories = CategoryManager.get_all_categories()
    for category in categories:
        category_name = category['name_en']
        
        # Get current month spending for this category
        category_expenses = [e for e in current_expenses if e['category'] == category_name]
        category_total = sum(expense['amount'] for expense in category_expenses)
        
        # Check against budget
        if category['budget'] > 0 and category_total > category['budget']:
            percentage_over = ((category_total - category['budget']) / category['budget']) * 100
            insights.append({
                'type': 'danger',
                'message': f'تجاوزت ميزانية {category["name_ar"]} بنسبة {percentage_over:.1f}%'
            })
        elif category['budget'] > 0 and category_total > (category['budget'] * 0.9):
            insights.append({
                'type': 'warning',
                'message': f'أنت قريب من تجاوز ميزانية {category["name_ar"]}'
            })
    
    # Add a generic insight if no specific ones were generated
    if not insights:
        insights.append({
            'type': 'info',
            'message': 'استمر في تتبع مصاريفك لرؤية تحليلات أكثر دقة'
        })
    
    return insights

def get_spending_alerts():
    """Generate spending alerts based on user's expenses"""
    alerts = []
    
    # Get current month's expenses
    today = datetime.now()
    start_of_month = datetime(today.year, today.month, 1).strftime('%Y-%m-%d')
    current_date = today.strftime('%Y-%m-%d')
    
    # Get previous month's date range
    first_of_prev_month = (datetime(today.year, today.month, 1) - timedelta(days=1)).replace(day=1)
    start_of_prev_month = first_of_prev_month.strftime('%Y-%m-%d')
    end_of_prev_month = (datetime(today.year, today.month, 1) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Get expenses
    current_month_expenses = ExpenseManager.get_expenses_by_date_range(start_of_month, current_date)
    previous_month_expenses = ExpenseManager.get_expenses_by_date_range(start_of_prev_month, end_of_prev_month)
    
    # Calculate days elapsed in current month
    days_elapsed = (today - datetime(today.year, today.month, 1)).days + 1
    days_in_month = (datetime(today.year, today.month + 1, 1) - datetime(today.year, today.month, 1)).days
    
    # Project monthly total based on current spending rate
    current_month_total = sum(expense['amount'] for expense in current_month_expenses)
    projected_month_total = (current_month_total / days_elapsed) * days_in_month
    
    previous_month_total = sum(expense['amount'] for expense in previous_month_expenses)
    
    # Alert if projected spending is 20% more than previous month
    if previous_month_total > 0 and projected_month_total > (previous_month_total * 1.2):
        increase_percentage = ((projected_month_total - previous_month_total) / previous_month_total) * 100
        alerts.append({
            'title': 'تنبيه الإنفاق!',
            'message': f'⚠️ معدل إنفاقك الحالي أعلى بنسبة {increase_percentage:.1f}% من الشهر الماضي. حاول خفض إنفاقك لتجنب تجاوز ميزانيتك.'
        })
    
    # Check for high spending categories
    categories = CategoryManager.get_all_categories()
    
    for category in categories:
        category_name = category['name_en']
        category_ar_name = category['name_ar']
        category_budget = category['budget']
        
        # Skip categories with no budget
        if category_budget <= 0:
            continue
        
        # Get current month spending for this category
        current_category_expenses = [e for e in current_month_expenses if e['category'] == category_name]
        current_category_total = sum(expense['amount'] for expense in current_category_expenses)
        
        # Project category total for the month
        projected_category_total = (current_category_total / days_elapsed) * days_in_month
        
        # Alert if projected spending is over budget
        if projected_category_total > category_budget:
            percentage_over = ((projected_category_total - category_budget) / category_budget) * 100
            alerts.append({
                'title': f'تنبيه {category_ar_name}!',
                'message': f'⚠️ من المتوقع أن تتجاوز ميزانية {category_ar_name} بنسبة {percentage_over:.1f}% بنهاية الشهر إذا استمر معدل الإنفاق الحالي.'
            })
    
    return alerts

def get_savings_tips():
    """Generate savings tips based on user's spending patterns"""
    tips = [
        {
            'title': 'التخطيط للوجبات',
            'message': 'خطط لوجباتك الأسبوعية مسبقًا واشترِ البقالة وفقًا لذلك. هذا يمكن أن يوفر ما يصل إلى 30% من نفقات الطعام الخاصة بك.'
        },
        {
            'title': 'استخدم المواصلات العامة',
            'message': 'فكر في استخدام المواصلات العامة بدلاً من سيارتك للرحلات القصيرة. هذا يوفر في تكاليف الوقود والصيانة.'
        },
        {
            'title': 'قاعدة 24 ساعة',
            'message': 'قبل إجراء عملية شراء كبيرة، انتظر 24 ساعة. غالبًا ما يساعدك هذا في تجنب المشتريات الاندفاعية.'
        },
        {
            'title': 'توفير الطاقة',
            'message': 'اخفض فاتورة الكهرباء الخاصة بك عن طريق إطفاء الأجهزة عند عدم استخدامها وتركيب مصابيح LED موفرة للطاقة.'
        },
        {
            'title': 'خفض نفقات الترفيه',
            'message': 'ابحث عن أنشطة ترفيهية مجانية أو منخفضة التكلفة. استكشف الحدائق المحلية والمتاحف والفعاليات المجتمعية.'
        }
    ]
    
    # Get current month's expenses by category
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
    
    # Add personalized tips based on spending
    if category_spending.get('Food', 0) > 0:
        tips.append({
            'title': 'وفر على الطعام',
            'message': 'تحضير وجبات المنزل يمكن أن يوفر لك الكثير. جرب تحضير وجبات الغداء للعمل بدلاً من شراء الطعام الجاهز.'
        })
    
    if category_spending.get('Shopping', 0) > 0:
        tips.append({
            'title': 'قارن الأسعار',
            'message': 'قبل شراء أي منتج، قارن الأسعار بين المتاجر المختلفة أو عبر الإنترنت. يمكنك توفير ما يصل إلى 20% بهذه الطريقة.'
        })
    
    if category_spending.get('Entertainment', 0) > 0:
        tips.append({
            'title': 'اشتراكات الترفيه',
            'message': 'راجع اشتراكاتك الشهرية (نتفليكس، سبوتيفاي، إلخ) وألغِ تلك التي لا تستخدمها بانتظام.'
        })
    
    # Return a random selection of 3 tips
    import random
    return random.sample(tips, min(3, len(tips)))
