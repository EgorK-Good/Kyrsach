from app import app, db
from models import User, Cuisine
from werkzeug.security import generate_password_hash

with app.app_context():
    # Create tables
    db.create_all()
    print("Database tables created")
    
    # Create admin user
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
    print("Admin user created")
    
    # Create cuisines
    cuisines = [
        Cuisine(name='Русская', description='Традиционная русская кухня с сытными супами, тушеными блюдами и пельменями.'),
        Cuisine(name='Армянская', description='Армянская кухня отличается свежими травами, специями и медленно приготовленными блюдами.'),
        Cuisine(name='Японская', description='Японская кухня подчеркивает свежие, сезонные ингредиенты с минимальной обработкой.'),
        Cuisine(name='Итальянская', description='Итальянская кухня известна своей пастой, пиццей, ризотто и региональными особенностями.')
    ]
    db.session.add_all(cuisines)
    db.session.commit()
    print("Default cuisines created")
