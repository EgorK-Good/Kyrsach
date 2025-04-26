from flask import render_template, flash, redirect, url_for, request, abort, jsonify, g
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User, Recipe, Cuisine, Favorite, Comment, Rating, Category, RecipePhoto
from forms import (LoginForm, RegistrationForm, RecipeForm, CuisineForm, SearchForm,
                  ProfileForm, AdminUserEditForm, CommentForm, RatingForm, RecipePhotoForm, CategoryForm)
import logging
import os
from datetime import datetime
from sqlalchemy import func, desc


# Загрузка глобальных данных перед каждым запросом
@app.before_request
def load_global_data():
    """Загружает данные, необходимые для всех шаблонов"""
    g.all_cuisines = Cuisine.query.all()


@app.route('/')
def index():
    # Get featured recipes (most recent)
    featured_recipes = Recipe.query.order_by(Recipe.created_at.desc()).limit(6).all()

    # Get all cuisines for navigation
    cuisines = Cuisine.query.all()

    return render_template('index.html', featured_recipes=featured_recipes, cuisines=cuisines)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash('Вход выполнен успешно!', 'success')
            return redirect(next_page or url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()

        if existing_user:
            flash('Имя пользователя уже занято. Пожалуйста, выберите другое.', 'danger')
        elif existing_email:
            flash('Email уже зарегистрирован. Пожалуйста, используйте другой email или войдите в систему.', 'danger')
        else:
            # Create new user
            hashed_password = generate_password_hash(form.password.data)
            user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=hashed_password,
                is_admin=False
            )
            db.session.add(user)
            db.session.commit()

            flash('Регистрация успешна! Пожалуйста, войдите в систему.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        # Check if username is changed and not already taken
        if form.username.data != current_user.username and User.query.filter_by(username=form.username.data).first():
            flash('Имя пользователя уже занято. Пожалуйста, выберите другое.', 'danger')
        # Check if email is changed and not already registered
        elif form.email.data != current_user.email and User.query.filter_by(email=form.email.data).first():
            flash('Email уже зарегистрирован. Пожалуйста, используйте другой email.', 'danger')
        else:
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.avatar = form.avatar.data
            current_user.bio = form.bio.data
            db.session.commit()
            flash('Профиль успешно обновлен!', 'success')
            return redirect(url_for('profile'))

    # Get user's recipes
    user_recipes = Recipe.query.filter_by(user_id=current_user.id).order_by(Recipe.created_at.desc()).all()

    # Get user's favorite recipes
    favorite_ids = [fav.recipe_id for fav in Favorite.query.filter_by(user_id=current_user.id).all()]
    favorite_recipes = Recipe.query.filter(Recipe.id.in_(favorite_ids)).all() if favorite_ids else []

    return render_template('profile.html', form=form, user_recipes=user_recipes, favorite_recipes=favorite_recipes)


@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    # Check if user is the recipe author or an admin
    if recipe.user_id != current_user.id and not current_user.is_admin:
        abort(403)  # Forbidden

    db.session.delete(recipe)
    db.session.commit()

    flash('Рецепт успешно удален!', 'success')
    return redirect(url_for('profile'))


@app.route('/toggle_favorite/<int:recipe_id>', methods=['POST'])
@login_required
def toggle_favorite(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    favorite = Favorite.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()

    if favorite:
        # Remove from favorites
        db.session.delete(favorite)
        db.session.commit()
        is_favorite = False
        message = 'Рецепт удален из избранного'
    else:
        # Add to favorites
        favorite = Favorite(user_id=current_user.id, recipe_id=recipe_id)
        db.session.add(favorite)
        db.session.commit()
        is_favorite = True
        message = 'Рецепт добавлен в избранное'

    # If the request was AJAX, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'is_favorite': is_favorite, 'message': message})

    # Otherwise redirect back to the recipe
    flash(message, 'success')
    return redirect(url_for('recipe_detail', recipe_id=recipe_id))


@app.route('/cuisine/<int:cuisine_id>')
def cuisine_recipes(cuisine_id):
    cuisine = Cuisine.query.get_or_404(cuisine_id)
    page = request.args.get('page', 1, type=int)

    # Получаем рецепты для выбранной кухни, сортируя по новизне
    query = Recipe.query.join(Recipe.cuisine).filter(Recipe.cuisine_id == cuisine_id).order_by(Recipe.created_at.desc())
    
    # Добавляем логирование для отладки
    app.logger.info(f'Cuisine {cuisine_id} recipe count: {query.count()}')
    
    # Проверяем количество рецептов
    if query.count() == 0:
        flash(f'В категории {cuisine.name} пока нет рецептов', 'info')
    
    recipes = query.paginate(page=page, per_page=9, error_out=False)

    # Форма поиска с выбором кухни
    form = SearchForm()
    form.cuisine.choices = [(0, 'Все кухни')] + [(c.id, c.name) for c in Cuisine.query.all()]
    form.cuisine.data = cuisine_id

    # Используем тот же шаблон для отображения
    return render_template('recipes.html', 
                           form=form, 
                           recipes=recipes, 
                           cuisine=cuisine,
                           title=f"{cuisine.name} кухня",
                           description=cuisine.description)


@app.route('/admin')
@login_required
def admin_dashboard():
    # Check if the user is an admin
    if not current_user.is_admin:
        abort(403)  # Forbidden

    users = User.query.all()
    recipes = Recipe.query.order_by(Recipe.created_at.desc()).all()
    cuisines = Cuisine.query.all()

    return render_template('admin_dashboard.html', users=users, recipes=recipes, cuisines=cuisines)


@app.route('/admin/add_cuisine', methods=['GET', 'POST'])
@login_required
def add_cuisine():
    # Check if the user is an admin
    if not current_user.is_admin:
        abort(403)  # Forbidden

    form = CuisineForm()

    if form.validate_on_submit():
        # Check if cuisine name already exists
        existing_cuisine = Cuisine.query.filter_by(name=form.name.data).first()

        if existing_cuisine:
            flash('Такая кухня уже существует!', 'danger')
        else:
            cuisine = Cuisine(name=form.name.data, description=form.description.data)
            db.session.add(cuisine)
            db.session.commit()

            flash('Кухня успешно добавлена!', 'success')
            return redirect(url_for('admin_dashboard'))

    return render_template('add_cuisine.html', form=form, title='Добавить новую кухню')


@app.route('/admin/delete_cuisine/<int:cuisine_id>', methods=['POST'])
@login_required
def delete_cuisine(cuisine_id):
    # Check if the user is an admin
    if not current_user.is_admin:
        abort(403)  # Forbidden

    cuisine = Cuisine.query.get_or_404(cuisine_id)

    # Check if any recipes are using this cuisine
    recipes_count = Recipe.query.filter_by(cuisine_id=cuisine_id).count()

    if recipes_count > 0:
        flash(f'Невозможно удалить кухню: с ней связано {recipes_count} рецептов.', 'danger')
    else:
        db.session.delete(cuisine)
        db.session.commit()
        flash('Кухня успешно удалена!', 'success')

    return redirect(url_for('admin_dashboard'))


@app.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
def toggle_admin(user_id):
    # Check if the current user is an admin
    if not current_user.is_admin:
        abort(403)  # Forbidden

    user = User.query.get_or_404(user_id)

    # Don't allow removing admin privileges from yourself
    if user.id == current_user.id:
        flash('Вы не можете отменить свои собственные права администратора.', 'danger')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()

        status = 'предоставлены' if user.is_admin else 'отозваны'
        flash(f'Права администратора {status} для {user.username}.', 'success')

    return redirect(url_for('admin_dashboard'))


@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    # Check if the current user is an admin
    if not current_user.is_admin:
        abort(403)  # Forbidden

    user = User.query.get_or_404(user_id)
    form = AdminUserEditForm(obj=user)

    if form.validate_on_submit():
        # Check if username is changed and not already taken
        if form.username.data != user.username and User.query.filter_by(username=form.username.data).first():
            flash('Имя пользователя уже занято. Пожалуйста, выберите другое.', 'danger')
        # Check if email is changed and not already registered
        elif form.email.data != user.email and User.query.filter_by(email=form.email.data).first():
            flash('Email уже зарегистрирован. Пожалуйста, используйте другой email.', 'danger')
        else:
            user.username = form.username.data
            user.email = form.email.data
            user.avatar = form.avatar.data
            user.bio = form.bio.data
            user.is_admin = form.is_admin.data

            db.session.commit()
            flash(f'Профиль пользователя {user.username} успешно обновлен!', 'success')
            return redirect(url_for('admin_dashboard'))

    return render_template('admin_edit_user.html', form=form, user=user)


@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    # Check if the current user is an admin
    if not current_user.is_admin:
        abort(403)  # Forbidden

    user = User.query.get_or_404(user_id)

    # Не позволяем удалить самого себя
    if user.id == current_user.id:
        flash('Вы не можете удалить свой собственный аккаунт.', 'danger')
        return redirect(url_for('admin_dashboard'))

    # Запоминаем имя для сообщения после удаления
    username = user.username

    # Удаляем пользователя (удаление рецептов и избранного произойдет автоматически благодаря каскадному удалению)
    db.session.delete(user)
    db.session.commit()

    flash(f'Пользователь {username} был успешно удален.', 'success')
    return redirect(url_for('admin_dashboard'))



# Маршруты для расширенных функций рецептов

@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    # Проверяем, добавлен ли рецепт в избранное
    is_favorite = False
    if current_user.is_authenticated:
        is_favorite = Favorite.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first() is not None

    # Получаем другие рецепты из той же кухни
    related_recipes = Recipe.query.filter_by(cuisine_id=recipe.cuisine_id).filter(Recipe.id != recipe_id).limit(3).all()

    # Получаем комментарии к рецепту
    comments = Comment.query.filter_by(recipe_id=recipe_id).order_by(Comment.created_at.desc()).all()

    # Формы для комментирования и рейтинга
    comment_form = CommentForm()
    rating_form = RatingForm()

    # Если пользователь авторизован, проверяем, оценивал ли он уже этот рецепт
    user_rating = None
    if current_user.is_authenticated:
        user_rating = Rating.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()
        if user_rating:
            rating_form.value.data = user_rating.value

    # Получаем дополнительные фотографии рецепта
    photos = RecipePhoto.query.filter_by(recipe_id=recipe_id).all()

    return render_template('recipe_detail.html', 
                          recipe=recipe, 
                          is_favorite=is_favorite, 
                          related_recipes=related_recipes,
                          comments=comments,
                          comment_form=comment_form,
                          rating_form=rating_form,
                          user_rating=user_rating,
                          photos=photos)


@app.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    form = RecipeForm()

    # Заполняем выбор кухни
    form.cuisine_id.choices = [(c.id, c.name) for c in Cuisine.query.all()]
    
    # Заполняем выбор категорий
    categories = Category.query.all()
    form.categories.choices = [(0, 'Без категории')] + [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        try:
            recipe = Recipe(
                title=form.title.data,
                description=form.description.data,
                ingredients=form.ingredients.data,
                instructions=form.instructions.data,
                prep_time=form.prep_time.data,
                cook_time=form.cook_time.data,
                servings=form.servings.data,
                difficulty=form.difficulty.data,
                cuisine_id=form.cuisine_id.data,
                user_id=current_user.id,
                image_url=form.image_url.data
            )

            try:
                db.session.add(recipe)
                db.session.commit()
                flash('Рецепт успешно добавлен!', 'success')
                return redirect(url_for('recipe_detail', recipe_id=recipe.id))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Ошибка при сохранении рецепта: {str(e)}")
                flash('Произошла ошибка при сохранении рецепта. Пожалуйста, попробуйте еще раз.', 'danger')
        except Exception as e:
            app.logger.error(f"Ошибка при создании рецепта: {str(e)}")
            flash('Произошла ошибка при создании рецепта. Пожалуйста, проверьте введенные данные.', 'danger')

    return render_template('add_recipe.html', form=form, title='Добавить новый рецепт')


@app.route('/edit_recipe/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    # Проверяем права доступа
    if recipe.user_id != current_user.id and not current_user.is_admin:
        abort(403)  # Доступ запрещен

    form = RecipeForm(obj=recipe)
    form.cuisine_id.choices = [(c.id, c.name) for c in Cuisine.query.all()]

    if request.method == 'GET':
        # Предзаполняем форму текущими данными
        form.title.data = recipe.title
        form.description.data = recipe.description
        form.ingredients.data = recipe.ingredients
        form.instructions.data = recipe.instructions
        form.prep_time.data = recipe.prep_time
        form.cook_time.data = recipe.cook_time
        form.servings.data = recipe.servings
        form.difficulty.data = recipe.difficulty
        form.cuisine_id.data = recipe.cuisine_id
        form.image_url.data = recipe.image_url

    # Заполняем категории, если они есть
    categories = Category.query.all()
    if categories:
        form.categories.choices = [(0, 'Без категории')] + [(c.id, c.name) for c in categories]
        # Устанавливаем текущую категорию
        current_category = recipe.categories.first()
        if current_category:
            form.categories.data = current_category.id

    if form.validate_on_submit():
        recipe.title = form.title.data
        recipe.description = form.description.data
        recipe.ingredients = form.ingredients.data
        recipe.instructions = form.instructions.data
        recipe.prep_time = form.prep_time.data
        recipe.cook_time = form.cook_time.data
        recipe.servings = form.servings.data
        recipe.difficulty = form.difficulty.data
        recipe.cuisine_id = form.cuisine_id.data

        # Обновляем URL изображения
        recipe.image_url = form.image_url.data

        # Обновляем категорию
        if form.categories.data != 0:  # Если выбрана категория
            # Удаляем все текущие категории
            for cat in list(recipe.categories):
                recipe.categories.remove(cat)

            # Добавляем новую категорию
            new_category = Category.query.get(form.categories.data)
            if new_category:
                recipe.categories.append(new_category)

        db.session.commit()
        flash('Рецепт успешно обновлен!', 'success')
        return redirect(url_for('recipe_detail', recipe_id=recipe.id))

    return render_template('edit_recipe.html', form=form, recipe=recipe, title='Редактировать рецепт')


# Маршруты для работы с комментариями

@app.route('/add_comment/<int:recipe_id>', methods=['POST'])
@login_required
def add_comment(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            recipe_id=recipe_id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Комментарий добавлен!', 'success')

    return redirect(url_for('recipe_detail', recipe_id=recipe_id))


@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    # Проверяем права доступа (автор комментария или админ)
    if comment.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    recipe_id = comment.recipe_id
    db.session.delete(comment)
    db.session.commit()

    flash('Комментарий удален!', 'success')
    return redirect(url_for('recipe_detail', recipe_id=recipe_id))


# Маршруты для работы с рейтингами

@app.route('/rate_recipe/<int:recipe_id>', methods=['POST'])
@login_required
def rate_recipe(recipe_id):
    if not current_user.is_authenticated:
        flash('Пожалуйста, войдите в систему, чтобы оценить рецепт.', 'warning')
        return redirect(url_for('login'))
        
    recipe = Recipe.query.get_or_404(recipe_id)
    form = RatingForm()

    try:
        if form.validate_on_submit():
            rating_value = int(form.value.data)
            if 1 <= rating_value <= 5:  # Проверяем что оценка от 1 до 5
                # Проверяем, есть ли уже оценка от этого пользователя
                existing_rating = Rating.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()

                if existing_rating:
                    # Обновляем существующую оценку
                    existing_rating.value = rating_value
                    db.session.commit()
                    flash('Ваша оценка обновлена!', 'success')
                else:
                    # Создаем новую оценку
                    rating = Rating(
                        value=rating_value,
                        user_id=current_user.id,
                        recipe_id=recipe_id
                    )
                    db.session.add(rating)
                    db.session.commit()
                    flash('Спасибо за вашу оценку!', 'success')
            else:
                flash('Оценка должна быть от 1 до 5', 'error')
        else:
            flash('Ошибка при сохранении оценки', 'error')
    except Exception as e:
        db.session.rollback()
        flash('Произошла ошибка при сохранении оценки', 'error')
        app.logger.error(f'Error saving rating: {str(e)}')

    return redirect(url_for('recipe_detail', recipe_id=recipe_id))


# Маршруты для работы с фотографиями рецептов

@app.route('/upload_recipe_photos/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def upload_recipe_photos(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    # Проверяем права доступа
    if recipe.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    form = RecipePhotoForm()

    if form.validate_on_submit():
        # Создаем запись о фото в БД
        recipe_photo = RecipePhoto(
            url=form.photo_url.data,
            caption=form.caption.data,
            recipe_id=recipe_id,
            user_id=current_user.id
        )
        db.session.add(recipe_photo)
        db.session.commit()

        flash('Фотография успешно добавлена!', 'success')
        return redirect(url_for('recipe_detail', recipe_id=recipe_id))

    return render_template('upload_photos.html', form=form, recipe=recipe)


@app.route('/delete_recipe_photo/<int:photo_id>', methods=['POST'])
@login_required
def delete_recipe_photo(photo_id):
    photo = RecipePhoto.query.get_or_404(photo_id)
    recipe_id = photo.recipe_id

    # Проверяем права доступа
    if photo.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    db.session.delete(photo)
    db.session.commit()

    flash('Фотография удалена!', 'success')
    return redirect(url_for('recipe_detail', recipe_id=recipe_id))


# Маршруты для категорий рецептов

@app.route('/admin/add_category', methods=['GET', 'POST'])
@login_required
def add_category():
    # Проверяем права администратора
    if not current_user.is_admin:
        abort(403)

    form = CategoryForm()

    if form.validate_on_submit():
        # Проверяем, существует ли уже такая категория
        existing_category = Category.query.filter_by(name=form.name.data).first()

        if existing_category:
            flash('Такая категория уже существует!', 'danger')
        else:
            category = Category(name=form.name.data, description=form.description.data)
            db.session.add(category)
            db.session.commit()

            flash('Категория успешно добавлена!', 'success')
            return redirect(url_for('admin_dashboard'))

    return render_template('add_category.html', form=form, title='Добавить новую категорию')


@app.route('/admin/delete_category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    # Проверяем права администратора
    if not current_user.is_admin:
        abort(403)

    category = Category.query.get_or_404(category_id)

    # Проверяем, используется ли эта категория
    if category.recipes.count() > 0:
        flash(f'Невозможно удалить категорию: с ней связано {category.recipes.count()} рецептов.', 'danger')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Категория успешно удалена!', 'success')

    return redirect(url_for('admin_dashboard'))


@app.route('/category/<int:category_id>')
def category_recipes(category_id):
    category = Category.query.get_or_404(category_id)

    # Получаем рецепты из выбранной категории, сортируя по новизне
    recipes_query = Recipe.query.join(Recipe.categories).filter(Category.id == category_id).order_by(Recipe.created_at.desc())

    # Пагинация
    page = request.args.get('page', 1, type=int)
    recipes = recipes_query.paginate(page=page, per_page=9, error_out=False)

    # Простая форма поиска
    form = SearchForm()

    return render_template('recipes.html', 
                          form=form, 
                          recipes=recipes, 
                          category=category,
                          title=f"Категория: {category.name}")


# Упрощенный маршрут для отображения рецептов

@app.route('/recipes')
def recipes():
    # Инициализируем форму поиска
    form = SearchForm()
    
    # Получаем все кухни для навигации и формы
    cuisines = Cuisine.query.all()
    form.cuisine.choices = [(0, 'Все кухни')] + [(c.id, c.name) for c in cuisines]
    
    # Получаем параметры фильтрации
    cuisine_id = request.args.get('cuisine', type=int)
    search_query = request.args.get('query', '')

    # Инициализируем базовый запрос
    query = Recipe.query

    # Применяем фильтры
    if cuisine_id:
        query = query.filter(Recipe.cuisine_id == cuisine_id)
    if search_query:
        query = query.filter(Recipe.title.ilike(f'%{search_query}%'))

    # Сортировка по новизне
    query = query.order_by(Recipe.created_at.desc())
    
    # Добавляем подробное логирование для отладки
    try:
        total_count = query.count()
        app.logger.info(f'Total recipes found: {total_count}')
        
        if cuisine_id:
            cuisine_recipes = query.filter_by(cuisine_id=cuisine_id).all()
            app.logger.info(f'Recipes for cuisine {cuisine_id}: {[r.title for r in cuisine_recipes]}')
        
        app.logger.info(f'SQL Query: {query}')
    except Exception as e:
        app.logger.error(f'Error in query execution: {str(e)}')
    app.logger.info(f'Recipe count: {query.count()}')

    # Проверяем, есть ли рецепты
    if query.count() == 0:
        flash('Рецепты пока не добавлены', 'info')

    # Пагинация
    page = request.args.get('page', 1, type=int)
    per_page = 9
    recipes = query.paginate(page=page, per_page=per_page, error_out=False)

    # Если выбрана конкретная кухня, получаем её данные
    selected_cuisine = None
    if cuisine_id:
        selected_cuisine = Cuisine.query.get_or_404(cuisine_id)

    app.logger.info(f'Found {query.count()} recipes')  # Добавляем логирование

    return render_template('recipes.html', 
                         form=form,
                         recipes=recipes,
                         cuisines=cuisines,
                         selected_cuisine=selected_cuisine)


# Маршрут для расшаривания рецепта в социальных сетях
@app.route('/share/<int:recipe_id>')
def share_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    # Генерируем URL для расшаривания
    recipe_url = url_for('recipe_detail', recipe_id=recipe_id, _external=True)

    # Подготавливаем параметры для разных соцсетей
    share_links = {
        'vk': f'https://vk.com/share.php?url={recipe_url}&title={recipe.title}',
        'telegram': f'https://t.me/share/url?url={recipe_url}&text={recipe.title}',
        'twitter': f'https://twitter.com/intent/tweet?url={recipe_url}&text={recipe.title}',
        'facebook': f'https://www.facebook.com/sharer/sharer.php?u={recipe_url}'
    }

    return render_template('share.html', recipe=recipe, share_links=share_links)


# Этот маршрут больше не используется, так как мы теперь используем прямые URL-ссылки на изображения


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404, message="Страница не найдена"), 404


@app.errorhandler(403)
def forbidden_error(error):
    return render_template('error.html', error_code=403, message="Доступ запрещен"), 403


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error_code=500, message="Внутренняя ошибка сервера"), 500