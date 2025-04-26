from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, SelectField, SubmitField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange, URL, ValidationError


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
    categories = SelectField('Категория', coerce=int, validators=[Optional()])
    image_url = StringField('URL изображения', validators=[DataRequired()], 
                           description='Введите URL адрес изображения (например, https://example.com/image.jpg)')
    submit = SubmitField('Сохранить рецепт')


class RecipePhotoForm(FlaskForm):
    photo_url = StringField('URL изображения', validators=[DataRequired()], 
                          description='Введите URL адрес изображения (например, https://example.com/image.jpg)')
    caption = StringField('Подпись к фотографии', validators=[Optional(), Length(max=128)])
    submit = SubmitField('Добавить фотографию')


class CuisineForm(FlaskForm):
    name = StringField('Название кухни', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Описание', validators=[Optional()])
    submit = SubmitField('Сохранить кухню')


class CategoryForm(FlaskForm):
    name = StringField('Название категории', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Описание', validators=[Optional()])
    submit = SubmitField('Сохранить категорию')


class SearchForm(FlaskForm):
    query = StringField('Поиск рецептов', validators=[Optional()])
    cuisine = SelectField('Кухня', coerce=int, validators=[Optional()], default=0)
    submit = SubmitField('Поиск')


class CommentForm(FlaskForm):
    content = TextAreaField('Ваш комментарий', validators=[DataRequired(), Length(min=3, max=1000)])
    submit = SubmitField('Добавить комментарий')


class RatingForm(FlaskForm):
    value = HiddenField('Оценка', validators=[DataRequired()])
    submit = SubmitField('Оценить')
    
    def validate_value(form, field):
        try:
            value = int(field.data)
            if value < 1 or value > 5:
                raise ValidationError('Пожалуйста, выберите оценку от 1 до 5')
        except ValueError:
            raise ValidationError('Пожалуйста, выберите корректную оценку')


class ProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    avatar = StringField('URL аватара', validators=[Optional(), Length(max=256)])
    bio = TextAreaField('О себе', validators=[Optional()])
    submit = SubmitField('Обновить профиль')


class AdminUserEditForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    avatar = StringField('URL аватара', validators=[Optional(), Length(max=256)])
    bio = TextAreaField('О себе', validators=[Optional()])
    is_admin = BooleanField('Администратор')
    submit = SubmitField('Сохранить изменения')
