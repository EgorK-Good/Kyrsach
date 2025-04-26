
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def populate_users():
    with app.app_context():
        # Создаем тестовых пользователей
        test_users = [
            {
                'username': 'maria_cook',
                'email': 'maria@example.com',
                'password': 'password123',
                'bio': 'Шеф-повар русской кухни с 10-летним опытом',
                'is_admin': False
            },
            {
                'username': 'alex_chef',
                'email': 'alex@example.com',
                'password': 'password123',
                'bio': 'Специалист по японской кухне',
                'is_admin': False
            },
            {
                'username': 'elena_gourmet',
                'email': 'elena@example.com',
                'password': 'password123',
                'bio': 'Эксперт армянской кухни',
                'is_admin': False
            },
            {
                'username': 'marco_italiano',
                'email': 'marco@example.com',
                'password': 'password123',
                'bio': 'Итальянский шеф-повар в третьем поколении',
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
