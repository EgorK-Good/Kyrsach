from app import app, db
from sqlalchemy import text
from models import Recipe, RecipePhoto

def update_image_url_columns():
    """
    Увеличивает размер полей image_url в таблицах Recipe и RecipePhoto до 1024 символов
    """
    try:
        with app.app_context():
            # Выполняем SQL запрос для изменения длины столбца image_url в таблице recipe
            db.session.execute(text('ALTER TABLE recipe ALTER COLUMN image_url TYPE VARCHAR(1024)'))
            
            # Выполняем SQL запрос для изменения длины столбца url в таблице recipe_photo
            db.session.execute(text('ALTER TABLE recipe_photo ALTER COLUMN url TYPE VARCHAR(1024)'))
            
            db.session.commit()
            print("Длина полей image_url и url успешно увеличена до 1024 символов!")
            
    except Exception as e:
        print(f"Ошибка при обновлении длины полей: {e}")

if __name__ == "__main__":
    update_image_url_columns()