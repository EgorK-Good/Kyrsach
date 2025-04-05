from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')


class RecipeForm(FlaskForm):
    title = StringField('Название рецепта', validators=[DataRequired(), Length(max=128)])
    description = TextAreaField('Описание', validators=[DataRequired()])
    ingredients = TextAreaField('Ингредиенты', validators=[DataRequired()])
    instructions = TextAreaField('Инструкции', validators=[DataRequired()])
    prep_time = IntegerField('Время подготовки (минуты)', validators=[DataRequired(), NumberRange(min=1)])
    cook_time = IntegerField('Время приготовления (минуты)', validators=[DataRequired(), NumberRange(min=1)])
    servings = IntegerField('Порции', validators=[DataRequired(), NumberRange(min=1)])
    difficulty = SelectField('Сложность', choices=[
        ('Легкий', 'Легкий'), 
        ('Средний', 'Средний'), 
        ('Сложный', 'Сложный')
    ], validators=[DataRequired()])
    cuisine_id = SelectField('Кухня', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Сохранить рецепт')


class CuisineForm(FlaskForm):
    name = StringField('Название кухни', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Описание', validators=[Optional()])
    submit = SubmitField('Сохранить кухню')


class SearchForm(FlaskForm):
    query = StringField('Поиск рецептов', validators=[Optional()])
    cuisine = SelectField('Кухня', coerce=int, validators=[Optional()], default=0)
    submit = SubmitField('Поиск')


class ProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Обновить профиль')
