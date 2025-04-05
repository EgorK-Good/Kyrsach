from app import app, db
from models import User
from werkzeug.security import generate_password_hash

# Данные для супер-пользователя
ADMIN_USERNAME = 'admin'
ADMIN_EMAIL = 'korejbaegor@gmail.com'
ADMIN_PASSWORD = '12345678egor'

with app.app_context():
    # Проверяем, существует ли уже такой пользователь
    existing_user = User.query.filter_by(email=ADMIN_EMAIL).first()
    
    if existing_user:
        # Если пользователь существует, но не имеет прав администратора
        if not existing_user.is_admin:
            existing_user.is_admin = True
            db.session.commit()
            print(f"Пользователь '{existing_user.username}' теперь имеет права администратора.")
        else:
            print(f"Пользователь '{existing_user.username}' уже является администратором.")
    else:
        # Создаем нового пользователя с правами администратора
        hashed_password = generate_password_hash(ADMIN_PASSWORD)
        admin_user = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password_hash=hashed_password,
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print(f"Администратор '{ADMIN_USERNAME}' успешно создан!")
        print(f"Email: {ADMIN_EMAIL}")
        print(f"Пароль: {ADMIN_PASSWORD}")
