import os
from app import app, db
from werkzeug.security import generate_password_hash

# Удаляем старую базу данных
db_path = 'instance/recipes.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Старая база данных удалена: {db_path}")

with app.app_context():
    # Создаем таблицы заново
    db.create_all()
    print("Таблицы базы данных созданы заново")
    
    # Создаем администратора
    from models import User, Cuisine
    
    admin = User(
        username='admin',
        email='korejbaegor@gmail.com',
        password_hash=generate_password_hash('12345678egor'),
        is_admin=True,
        avatar='default_avatar.png',
        bio='Администратор сайта'
    )
    db.session.add(admin)
    db.session.commit()
    print("Администратор создан")
    
    # Создаем кухни
    cuisines = [
        Cuisine(name='Русская', description='Традиционная русская кухня с сытными супами, тушеными блюдами и пельменями.'),
        Cuisine(name='Армянская', description='Армянская кухня отличается свежими травами, специями и медленно приготовленными блюдами.'),
        Cuisine(name='Японская', description='Японская кухня подчеркивает свежие, сезонные ингредиенты с минимальной обработкой.'),
        Cuisine(name='Итальянская', description='Итальянская кухня известна своей пастой, пиццей, ризотто и региональными особенностями.')
    ]
    db.session.add_all(cuisines)
    db.session.commit()
    print("Созданы кухни по умолчанию")
    
    print("База данных успешно перестроена!")
