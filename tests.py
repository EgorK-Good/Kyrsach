
import unittest
from app import app, db
from models import User, Recipe, Cuisine, Rating, Comment
from werkzeug.security import generate_password_hash

class RecipeAppTests(unittest.TestCase):
    def setUp(self):
        # Настройка тестовой базы данных
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            
            # Создаем тестового пользователя
            test_user = User(
                username='testuser',
                email='test@test.com',
                password_hash=generate_password_hash('testpass'),
                is_admin=False
            )
            db.session.add(test_user)
            
            # Создаем тестовую кухню
            test_cuisine = Cuisine(
                name='Тестовая кухня',
                description='Описание тестовой кухни'
            )
            db.session.add(test_cuisine)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        response = self.app.post('/login', data=dict(
            username='testuser',
            password='testpass'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_add_recipe(self):
        # Сначала логинимся
        self.app.post('/login', data=dict(
            username='testuser',
            password='testpass'
        ))
        
        # Добавляем рецепт
        response = self.app.post('/add_recipe', data=dict(
            title='Тестовый рецепт',
            description='Описание тестового рецепта',
            ingredients='Ингредиент 1\nИнгредиент 2',
            instructions='Шаг 1\nШаг 2',
            prep_time=30,
            cook_time=45,
            servings=4,
            difficulty='Средний',
            cuisine_id=1
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_recipe_api(self):
        response = self.app.get('/api/recipes')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('recipes' in response.get_json())

if __name__ == '__main__':
    unittest.main()
