from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Column, String, func


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    avatar = db.Column(db.String(256), default='default_avatar.png')  # URL или путь к аватарке пользователя
    bio = db.Column(db.Text, nullable=True)  # Биография пользователя
    recipes = db.relationship('Recipe', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'


class Cuisine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text)
    recipes = db.relationship('Recipe', backref='cuisine', lazy='dynamic')
    
    def __repr__(self):
        return f'<Cuisine {self.name}>'


# Связующая таблица для рецептов и категорий (для расширенной фильтрации)
recipe_category = db.Table('recipe_category',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text)
    recipes = db.relationship('Recipe', secondary=recipe_category, backref=db.backref('categories', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    prep_time = db.Column(db.Integer)  # в минутах
    cook_time = db.Column(db.Integer)  # в минутах
    servings = db.Column(db.Integer)
    difficulty = db.Column(db.String(20))  # Легкий, Средний, Сложный
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cuisine_id = db.Column(db.Integer, db.ForeignKey('cuisine.id'))
    image_url = db.Column(db.String(1024))  # Добавляем поле для URL изображения
    
    # Связи с другими таблицами
    favorites = db.relationship('Favorite', backref='recipe', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='recipe', lazy='dynamic', cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='recipe', lazy='dynamic', cascade='all, delete-orphan')
    photos = db.relationship('RecipePhoto', backref='recipe', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def average_rating(self):
        """Вычисляет средний рейтинг рецепта"""
        result = db.session.query(func.avg(Rating.value)).filter(Rating.recipe_id == self.id).scalar()
        return round(result, 1) if result else 0
    
    @property
    def rating_count(self):
        """Возвращает количество оценок рецепта"""
        return self.ratings.count()
    
    def __repr__(self):
        return f'<Recipe {self.title}>'


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='user_recipe_uc'),)
    
    def __repr__(self):
        return f'<Favorite {self.user_id}:{self.recipe_id}>'


# Новые модели для комментариев, рейтингов и фотографий

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    
    def __repr__(self):
        return f'<Comment {self.id} by {self.author.username}>'


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)  # От 1 до 5
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False, index=True)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='user_recipe_rating_uc'),)
    
    def __repr__(self):
        return f'<Rating {self.value} by {self.user_id} for {self.recipe_id}>'


class RecipePhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(1024), nullable=False)  # Увеличена длина до 1024 символов
    caption = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('photos', lazy='dynamic'))
    
    def __repr__(self):
        return f'<RecipePhoto {self.id} for {self.recipe_id}>'
