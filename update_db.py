import sqlite3
from app import app, db

def add_columns_to_user_table():
    """
    Добавление новых столбцов в таблицу user, если они не существуют
    """
    try:
        with app.app_context():
            # Проверяем, существует ли база данных
            conn = sqlite3.connect('instance/recipes.db')
            cursor = conn.cursor()
            
            # Проверяем, есть ли столбец avatar
            cursor.execute("PRAGMA table_info(user)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Добавляем столбец avatar, если его нет
            if 'avatar' not in columns:
                print("Добавление столбца 'avatar' в таблицу 'user'...")
                cursor.execute("ALTER TABLE user ADD COLUMN avatar TEXT DEFAULT 'default_avatar.png'")
            
            # Добавляем столбец bio, если его нет
            if 'bio' not in columns:
                print("Добавление столбца 'bio' в таблицу 'user'...")
                cursor.execute("ALTER TABLE user ADD COLUMN bio TEXT")
            
            conn.commit()
            conn.close()
            print("База данных успешно обновлена!")
            
    except Exception as e:
        print(f"Ошибка при обновлении базы данных: {e}")

if __name__ == "__main__":
    add_columns_to_user_table()
