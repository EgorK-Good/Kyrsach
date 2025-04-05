from flask import render_template, flash, redirect, url_for, request, abort, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User, Recipe, Cuisine, Favorite
from forms import LoginForm, RegistrationForm, RecipeForm, CuisineForm, SearchForm, ProfileForm
import logging


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
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
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
            flash('Username already taken. Please choose another.', 'danger')
        elif existing_email:
            flash('Email already registered. Please use another email or log in.', 'danger')
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
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html', form=form)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        # Check if username is changed and not already taken
        if form.username.data != current_user.username and User.query.filter_by(username=form.username.data).first():
            flash('Username already taken. Please choose another.', 'danger')
        # Check if email is changed and not already registered
        elif form.email.data != current_user.email and User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please use another email.', 'danger')
        else:
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
    
    # Get user's recipes
    user_recipes = Recipe.query.filter_by(user_id=current_user.id).order_by(Recipe.created_at.desc()).all()
    
    # Get user's favorite recipes
    favorite_ids = [fav.recipe_id for fav in Favorite.query.filter_by(user_id=current_user.id).all()]
    favorite_recipes = Recipe.query.filter(Recipe.id.in_(favorite_ids)).all() if favorite_ids else []
    
    return render_template('profile.html', form=form, user_recipes=user_recipes, favorite_recipes=favorite_recipes)


@app.route('/recipes')
def recipes():
    # Initialize search form
    form = SearchForm()
    
    # Populate cuisine choices for the form
    cuisines = Cuisine.query.all()
    form.cuisine.choices = [(0, 'All Cuisines')] + [(c.id, c.name) for c in cuisines]
    
    # Get filter parameters
    cuisine_id = request.args.get('cuisine', 0, type=int)
    search_query = request.args.get('query', '')
    
    # Initialize base query
    query = Recipe.query
    
    # Apply filters
    if cuisine_id:
        query = query.filter_by(cuisine_id=cuisine_id)
        form.cuisine.data = cuisine_id
    
    if search_query:
        form.query.data = search_query
        query = query.filter(Recipe.title.ilike(f'%{search_query}%'))
    
    # Get recipes with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 9  # Number of recipes per page
    recipes_pagination = query.order_by(Recipe.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('recipes.html', form=form, recipes=recipes_pagination, cuisines=cuisines)


@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    
    # Check if the current user has favorited this recipe
    is_favorite = False
    if current_user.is_authenticated:
        is_favorite = Favorite.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first() is not None
    
    # Get other recipes from the same cuisine
    related_recipes = Recipe.query.filter_by(cuisine_id=recipe.cuisine_id).filter(Recipe.id != recipe_id).limit(3).all()
    
    return render_template('recipe_detail.html', recipe=recipe, is_favorite=is_favorite, related_recipes=related_recipes)


@app.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    form = RecipeForm()
    
    # Populate cuisine choices for the form
    form.cuisine_id.choices = [(c.id, c.name) for c in Cuisine.query.all()]
    
    if form.validate_on_submit():
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
            user_id=current_user.id
        )
        db.session.add(recipe)
        db.session.commit()
        
        flash('Recipe added successfully!', 'success')
        return redirect(url_for('recipe_detail', recipe_id=recipe.id))
    
    return render_template('add_recipe.html', form=form, title='Add New Recipe')


@app.route('/edit_recipe/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    
    # Check if user is the recipe author or an admin
    if recipe.user_id != current_user.id and not current_user.is_admin:
        abort(403)  # Forbidden
    
    form = RecipeForm(obj=recipe)
    form.cuisine_id.choices = [(c.id, c.name) for c in Cuisine.query.all()]
    
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
        
        db.session.commit()
        flash('Recipe updated successfully!', 'success')
        return redirect(url_for('recipe_detail', recipe_id=recipe.id))
    
    return render_template('edit_recipe.html', form=form, recipe=recipe, title='Edit Recipe')


@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    
    # Check if user is the recipe author or an admin
    if recipe.user_id != current_user.id and not current_user.is_admin:
        abort(403)  # Forbidden
    
    db.session.delete(recipe)
    db.session.commit()
    
    flash('Recipe deleted successfully!', 'success')
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
        message = 'Recipe removed from favorites'
    else:
        # Add to favorites
        favorite = Favorite(user_id=current_user.id, recipe_id=recipe_id)
        db.session.add(favorite)
        db.session.commit()
        is_favorite = True
        message = 'Recipe added to favorites'
    
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
    recipes = Recipe.query.filter_by(cuisine_id=cuisine_id).paginate(page=page, per_page=9, error_out=False)
    
    return render_template('recipes.html', recipes=recipes, cuisine=cuisine, cuisines=Cuisine.query.all())


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
            flash('Cuisine already exists!', 'danger')
        else:
            cuisine = Cuisine(name=form.name.data, description=form.description.data)
            db.session.add(cuisine)
            db.session.commit()
            
            flash('Cuisine added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
    
    return render_template('add_recipe.html', form=form, title='Add New Cuisine')


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
        flash(f'Cannot delete cuisine: {recipes_count} recipes are associated with it.', 'danger')
    else:
        db.session.delete(cuisine)
        db.session.commit()
        flash('Cuisine deleted successfully!', 'success')
    
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
        flash('You cannot remove your own admin privileges.', 'danger')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        
        status = 'granted' if user.is_admin else 'revoked'
        flash(f'Admin privileges {status} for {user.username}.', 'success')
    
    return redirect(url_for('admin_dashboard'))


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404, message="Page not found"), 404


@app.errorhandler(403)
def forbidden_error(error):
    return render_template('error.html', error_code=403, message="Access forbidden"), 403


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error_code=500, message="Internal server error"), 500