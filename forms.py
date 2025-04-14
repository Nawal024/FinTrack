from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired(message='يرجى إدخال اسم المستخدم')])
    password = PasswordField('كلمة المرور', validators=[DataRequired(message='يرجى إدخال كلمة المرور')])
    remember_me = BooleanField('تذكرني')
    submit = SubmitField('تسجيل الدخول')

class RegistrationForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[
        DataRequired(message='يرجى إدخال اسم المستخدم'),
        Length(min=3, max=64, message='يجب أن يكون اسم المستخدم بين 3 و 64 حرفًا')
    ])
    email = EmailField('البريد الإلكتروني', validators=[
        DataRequired(message='يرجى إدخال البريد الإلكتروني'),
        Email(message='يرجى إدخال بريد إلكتروني صالح'),
        Length(max=120, message='البريد الإلكتروني طويل جدًا')
    ])
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(message='يرجى إدخال كلمة المرور'),
        Length(min=8, message='يجب أن تكون كلمة المرور 8 أحرف على الأقل')
    ])
    password2 = PasswordField('تأكيد كلمة المرور', validators=[
        DataRequired(message='يرجى تأكيد كلمة المرور'),
        EqualTo('password', message='كلمات المرور غير متطابقة')
    ])
    submit = SubmitField('تسجيل')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('يرجى استخدام اسم مستخدم آخر')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('يرجى استخدام بريد إلكتروني آخر')