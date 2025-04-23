import sqlite3

# Подключение к вашей базе данных
conn = sqlite3.connect('recipes.db')
cursor = conn.cursor()

# Добавление колонки image_url
cursor.execute('ALTER TABLE recipe ADD COLUMN image_url TEXT;')

# Сохранение изменений и закрытие соединения
conn.commit()
conn.close()
