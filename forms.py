from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class RecipeForm(FlaskForm):
    title = StringField('Recipe Title', validators=[DataRequired(), Length(max=128)])
    description = TextAreaField('Description', validators=[DataRequired()])
    ingredients = TextAreaField('Ingredients', validators=[DataRequired()])
    instructions = TextAreaField('Instructions', validators=[DataRequired()])
    prep_time = IntegerField('Preparation Time (minutes)', validators=[DataRequired(), NumberRange(min=1)])
    cook_time = IntegerField('Cooking Time (minutes)', validators=[DataRequired(), NumberRange(min=1)])
    servings = IntegerField('Servings', validators=[DataRequired(), NumberRange(min=1)])
    difficulty = SelectField('Difficulty', choices=[
        ('Easy', 'Easy'), 
        ('Medium', 'Medium'), 
        ('Hard', 'Hard')
    ], validators=[DataRequired()])
    cuisine_id = SelectField('Cuisine', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Recipe')


class CuisineForm(FlaskForm):
    name = StringField('Cuisine Name', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save Cuisine')


class SearchForm(FlaskForm):
    query = StringField('Search Recipes', validators=[Optional()])
    cuisine = SelectField('Cuisine', coerce=int, validators=[Optional()], default=0)
    submit = SubmitField('Search')


class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Profile')
