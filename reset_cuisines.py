from app import app, db
from models import Cuisine

with app.app_context():
    # Удаляем существующие кухни
    Cuisine.query.delete()
    db.session.commit()
    
    # Добавляем кухни с переводом на русский
    cuisines = [
        Cuisine(name='Русская', description='Традиционная русская кухня с сытными супами, тушеными блюдами и пельменями.'),
        Cuisine(name='Армянская', description='Армянская кухня отличается свежими травами, специями и медленно приготовленными блюдами.'),
        Cuisine(name='Японская', description='Японская кухня подчеркивает свежие, сезонные ингредиенты с минимальной обработкой.'),
        Cuisine(name='Итальянская', description='Итальянская кухня известна своей пастой, пиццей, ризотто и региональными особенностями.')
    ]
    db.session.add_all(cuisines)
    db.session.commit()
    print("Кухни успешно обновлены!")
