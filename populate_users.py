
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def populate_users():
    with app.app_context():
        # Создаем тестовых пользователей
        test_users = [
            {
                'username': 'maria',
                'email': 'maria@example.com',
                'password': 'password123',
                'bio': 'Люблю готовить русскую кухню',
                'is_admin': False
            },
            {
                'username': 'alex',
                'email': 'alex@example.com',
                'password': 'password123',
                'bio': 'Шеф-повар японской кухни',
                'is_admin': False
            },
            {
                'username': 'elena',
                'email': 'elena@example.com',
                'password': 'password123',
                'bio': 'Специалист по армянской кухне',
                'is_admin': False
            }
        ]

        for user_data in test_users:
            user = User.query.filter_by(username=user_data['username']).first()
            if not user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    bio=user_data['bio'],
                    is_admin=user_data['is_admin']
                )
                db.session.add(user)
        
        db.session.commit()
        print("Тестовые пользователи успешно добавлены!")

if __name__ == '__main__':
    populate_users()
