from app import app, db
from models import Recipe, Cuisine
from datetime import datetime

def populate_recipes():
    with app.app_context():
        # Русская кухня
        russian = Cuisine.query.filter_by(name='Русская').first()
        russian_recipes = [
            {
                'title': 'Борщ классический',
                'description': 'Традиционный русский суп с насыщенным вкусом свеклы и говядины',
                'ingredients': '- Говядина 500г\n- Свекла 2шт\n- Капуста 300г\n- Картофель 3шт\n- Морковь 1шт\n- Лук 1шт\n- Томатная паста 2ст.л.\n- Специи по вкусу',
                'instructions': '1. Сварить бульон из говядины\n2. Обжарить овощи\n3. Добавить нашинкованную капусту\n4. Добавить свеклу и томатную пасту\n5. Варить до готовности',
                'prep_time': 30,
                'cook_time': 120,
                'servings': 6,
                'difficulty': 'Средний',
                'image_url': 'https://images.unsplash.com/photo-1550367083-9fa5596e89e5?w=800'
            },
            {
                'title': 'Пельмени домашние',
                'description': 'Сочные пельмени с мясной начинкой по старинному рецепту',
                'ingredients': '- Мука 600г\n- Яйца 2шт\n- Вода 200мл\n- Фарш 500г\n- Лук 2шт\n- Соль, перец по вкусу',
                'instructions': '1. Замесить тесто\n2. Приготовить начинку\n3. Слепить пельмени\n4. Варить в подсоленной воде 7-8 минут',
                'prep_time': 60,
                'cook_time': 10,
                'servings': 6,
                'difficulty': 'Сложный',
                'image_url': 'https://images.unsplash.com/photo-1556906851-a2b19ba19edf?w=800'
            },
            {
                'title': 'Блины русские',
                'description': 'Тонкие ажурные блины на молоке',
                'ingredients': '- Молоко 1л\n- Мука 400г\n- Яйца 3шт\n- Сахар 2ст.л.\n- Масло растительное 50мл',
                'instructions': '1. Смешать все ингредиенты\n2. Выпекать на разогретой сковороде\n3. Подавать со сметаной',
                'prep_time': 15,
                'cook_time': 30,
                'servings': 4,
                'difficulty': 'Средний',
                'image_url': 'https://images.unsplash.com/photo-1551240122-5f73d6eaca84?w=800'
            },
            {
                'title': 'Оливье',
                'description': 'Традиционный новогодний салат',
                'ingredients': '- Картофель 4шт\n- Морковь 2шт\n- Яйца 4шт\n- Колбаса 300г\n- Огурцы маринованные 4шт\n- Горошек 1 банка\n- Майонез',
                'instructions': '1. Отварить овощи и яйца\n2. Нарезать кубиками\n3. Смешать с майонезом',
                'prep_time': 40,
                'cook_time': 30,
                'servings': 8,
                'difficulty': 'Легкий',
                'image_url': 'https://images.unsplash.com/photo-1547496502-affa22e38842?w=800'
            },
            {
                'title': 'Щи из свежей капусты',
                'description': 'Легкий суп на мясном бульоне',
                'ingredients': '- Капуста 500г\n- Морковь 1шт\n- Лук 1шт\n- Картофель 3шт\n- Мясо 400г\n- Специи по вкусу',
                'instructions': '1. Сварить бульон\n2. Нашинковать капусту\n3. Добавить овощи\n4. Варить до готовности',
                'prep_time': 20,
                'cook_time': 90,
                'servings': 6,
                'difficulty': 'Легкий',
                'image_url': 'https://images.unsplash.com/photo-1547592180-85f173990554?w=800'
            }
        ]

        # Армянская кухня
        armenian = Cuisine.query.filter_by(name='Армянская').first()
        armenian_recipes = [
            {
                'title': 'Долма',
                'description': 'Виноградные листья, фаршированные мясом и рисом',
                'ingredients': '- Виноградные листья 200г\n- Фарш 500г\n- Рис 100г\n- Лук 2шт\n- Зелень\n- Специи',
                'instructions': '1. Подготовить листья\n2. Смешать начинку\n3. Завернуть долму\n4. Тушить 40 минут',
                'prep_time': 60,
                'cook_time': 40,
                'servings': 6,
                'difficulty': 'Сложный',
                'image_url': 'https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=800'
            },
            {
                'title': 'Хаш',
                'description': 'Наваристый суп из говяжьих ножек',
                'ingredients': '- Говяжьи ножки 2кг\n- Чеснок\n- Лаваш\n- Соль',
                'instructions': '1. Варить ножки 8 часов\n2. Подавать с чесноком\n3. Добавить соль по вкусу',
                'prep_time': 30,
                'cook_time': 480,
                'servings': 8,
                'difficulty': 'Средний',
                'image_url': 'https://images.unsplash.com/photo-1583835746434-cf1534674b41?w=800'
            },
            {
                'title': 'Ламаджо',
                'description': 'Тонкая лепешка с мясной начинкой',
                'ingredients': '- Мука 400г\n- Фарш 300г\n- Помидоры 2шт\n- Перец\n- Специи',
                'instructions': '1. Замесить тесто\n2. Приготовить начинку\n3. Выпекать в духовке',
                'prep_time': 40,
                'cook_time': 15,
                'servings': 4,
                'difficulty': 'Средний',
                'image_url': 'https://images.unsplash.com/photo-1576867757603-05b134ebc379?w=800'
            },
            {
                'title': 'Хачапури по-армянски',
                'description': 'Лепешка с сыром',
                'ingredients': '- Мука 500г\n- Сыр 400г\n- Яйца 2шт\n- Масло 50г',
                'instructions': '1. Замесить тесто\n2. Завернуть сыр\n3. Выпекать до золотистого цвета',
                'prep_time': 30,
                'cook_time': 20,
                'servings': 4,
                'difficulty': 'Средний',
                'image_url': 'https://images.unsplash.com/photo-1628689469838-524a4a973b31?w=800'
            },
            {
                'title': 'Кюфта',
                'description': 'Отбивные из говядины',
                'ingredients': '- Говядина 600г\n- Лук 2шт\n- Специи\n- Зелень',
                'instructions': '1. Отбить мясо\n2. Приготовить фарш\n3. Жарить на гриле',
                'prep_time': 40,
                'cook_time': 20,
                'servings': 4,
                'difficulty': 'Сложный',
                'image_url': 'https://images.unsplash.com/photo-1529042410759-befb1204b468?w=800'
            }
        ]

        # Японская кухня
        japanese = Cuisine.query.filter_by(name='Японская').first()
        japanese_recipes = [
            {
                'title': 'Суши роллы "Филадельфия"',
                'description': 'Классические роллы с лососем и сливочным сыром',
                'ingredients': '- Рис 400г\n- Лосось 200г\n- Сливочный сыр 100г\n- Нори 4 листа\n- Огурец',
                'instructions': '1. Приготовить рис\n2. Собрать роллы\n3. Нарезать порционно',
                'prep_time': 40,
                'cook_time': 20,
                'servings': 4,
                'difficulty': 'Сложный',
                'image_url': 'https://images.unsplash.com/photo-1553621042-f6e147245754?w=800'
            },
            {
                'title': 'Рамен',
                'description': 'Суп с пшеничной лапшой',
                'ingredients': '- Лапша 400г\n- Свинина 300г\n- Яйца 4шт\n- Водоросли\n- Соевый соус',
                'instructions': '1. Сварить бульон\n2. Приготовить лапшу\n3. Собрать суп',
                'prep_time': 30,
                'cook_time': 180,
                'servings': 4,
                'difficulty': 'Средний',
                'image_url': 'https://images.unsplash.com/photo-1557872943-16a5ac26437e?w=800'
            },
            {
                'title': 'Темпура',
                'description': 'Креветки в кляре',
                'ingredients': '- Креветки 500г\n- Мука 200г\n- Яйцо\n- Масло для жарки',
                'instructions': '1. Приготовить кляр\n2. Обжарить креветки\n3. Подавать с соусом',
                'prep_time': 20,
                'cook_time': 15,
                'servings': 4,
                'difficulty': 'Средний',
                'image_url': 'https://images.unsplash.com/photo-1629684782790-8ffb26067537?w=800'
            },
            {
                'title': 'Мисо суп',
                'description': 'Традиционный японский суп',
                'ingredients': '- Паста мисо 100г\n- Тофу 200г\n- Водоросли\n- Лук зеленый',
                'instructions': '1. Вскипятить воду\n2. Добавить пасту мисо\n3. Добавить остальные ингредиенты',
                'prep_time': 10,
                'cook_time': 15,
                'servings': 4,
                'difficulty': 'Легкий',
                'image_url': 'https://images.unsplash.com/photo-1607301405390-d831c242f59b?w=800'
            },
            {
                'title': 'Якитори',
                'description': 'Куриные шашлычки',
                'ingredients': '- Куриное филе 500г\n- Соевый соус\n- Мирин\n- Сахар',
                'instructions': '1. Замариновать мясо\n2. Нанизать на шпажки\n3. Жарить на гриле',
                'prep_time': 30,
                'cook_time': 15,
                'servings': 4,
                'difficulty': 'Легкий',
                'image_url': 'https://images.unsplash.com/photo-1630698467837-b4f432fd3971?w=800'
            }
        ]

        # Итальянская кухня
        italian = Cuisine.query.filter_by(name='Итальянская').first()
        italian_recipes = [
            {
                'title': 'Паста Карбонара',
                'description': 'Классическая паста с беконом и сыром',
                'ingredients': '- Спагетти 400г\n- Бекон 200г\n- Яйца 4шт\n- Пармезан 100г\n- Перец черный',
                'instructions': '1. Отварить пасту\n2. Обжарить бекон\n3. Смешать с соусом',
                'prep_time': 15,
                'cook_time': 20,
                'servings': 4,
                'difficulty': 'Средний',
                'image_url': 'https://images.unsplash.com/photo-1612874742237-6526221588e3?w=800'
            },
            {
                'title': 'Пицца Маргарита',
                'description': 'Традиционная пицца с томатами и моцареллой',
                'ingredients': '- Тесто для пиццы\n- Томаты 400г\n- Моцарелла 200г\n- Базилик\n- Оливковое масло',
                'instructions': '1. Раскатать тесто\n2. Выложить начинку\n3. Выпекать при высокой температуре',
                'prep_time': 30,
                'cook_time': 15,
                'servings': 4,
                'difficulty': 'Средний',
                'image_url': 'https://images.unsplash.com/photo-1604068549290-dea0e4a305ca?w=800'
            },
            {
                'title': 'Тирамису',
                'description': 'Десерт с кофе и маскарпоне',
                'ingredients': '- Печенье савоярди\n- Маскарпоне 500г\n- Кофе\n- Какао\n- Яйца',
                'instructions': '1. Приготовить крем\n2. Пропитать печенье\n3. Собрать десерт слоями',
                'prep_time': 30,
                'cook_time': 0,
                'servings': 6,
                'difficulty': 'Средний',
                'image_url': 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=800'
            },
            {
                'title': 'Ризотто с грибами',
                'description': 'Кремовый рис с белыми грибами',
                'ingredients': '- Рис арборио 400г\n- Грибы 300г\n- Лук\n- Вино белое\n- Бульон',
                'instructions': '1. Обжарить грибы\n2. Готовить рис\n3. Добавлять бульон постепенно',
                'prep_time': 20,
                'cook_time': 40,
                'servings': 4,
                'difficulty': 'Сложный',
                'image_url': 'https://images.unsplash.com/photo-1595908129746-57ca1a63dd4d?w=800'
            },
            {
                'title': 'Лазанья',
                'description': 'Слоеное блюдо с мясом и соусом бешамель',
                'ingredients': '- Листы для лазаньи\n- Фарш 500г\n- Соус бешамель\n- Сыр\n- Томатный соус',
                'instructions': '1. Приготовить соусы\n2. Собрать слоями\n3. Запекать в духовке',
                'prep_time': 45,
                'cook_time': 45,
                'servings': 6,
                'difficulty': 'Сложный',
                'image_url': 'https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=800'
            }
        ]

        # Добавляем все рецепты в базу данных
        for recipe_data in russian_recipes:
            recipe = Recipe(
                title=recipe_data['title'],
                description=recipe_data['description'],
                ingredients=recipe_data['ingredients'],
                instructions=recipe_data['instructions'],
                prep_time=recipe_data['prep_time'],
                cook_time=recipe_data['cook_time'],
                servings=recipe_data['servings'],
                difficulty=recipe_data['difficulty'],
                cuisine_id=russian.id,
                user_id=1,  # ID администратора
                image_url=recipe_data['image_url']
            )
            db.session.add(recipe)

        for recipe_data in armenian_recipes:
            recipe = Recipe(
                title=recipe_data['title'],
                description=recipe_data['description'],
                ingredients=recipe_data['ingredients'],
                instructions=recipe_data['instructions'],
                prep_time=recipe_data['prep_time'],
                cook_time=recipe_data['cook_time'],
                servings=recipe_data['servings'],
                difficulty=recipe_data['difficulty'],
                cuisine_id=armenian.id,
                user_id=4,  # Elena (армянские рецепты)
                image_url=recipe_data['image_url']
            )
            db.session.add(recipe)

        for recipe_data in japanese_recipes:
            recipe = Recipe(
                title=recipe_data['title'],
                description=recipe_data['description'],
                ingredients=recipe_data['ingredients'],
                instructions=recipe_data['instructions'],
                prep_time=recipe_data['prep_time'],
                cook_time=recipe_data['cook_time'],
                servings=recipe_data['servings'],
                difficulty=recipe_data['difficulty'],
                cuisine_id=japanese.id,
                user_id=1,
                image_url=recipe_data['image_url']
            )
            db.session.add(recipe)

        for recipe_data in italian_recipes:
            recipe = Recipe(
                title=recipe_data['title'],
                description=recipe_data['description'],
                ingredients=recipe_data['ingredients'],
                instructions=recipe_data['instructions'],
                prep_time=recipe_data['prep_time'],
                cook_time=recipe_data['cook_time'],
                servings=recipe_data['servings'],
                difficulty=recipe_data['difficulty'],
                cuisine_id=italian.id,
                user_id=1,
                image_url=recipe_data['image_url']
            )
            db.session.add(recipe)

        db.session.commit()
        print("Рецепты успешно добавлены в базу данных!")

if __name__ == '__main__':
    populate_recipes()