"""
Management command to seed the database with sample menu data.
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from menu.models import Category, MenuItem


class Command(BaseCommand):
    help = 'Seeds the database with sample categories and menu items'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Create Categories
        categories_data = [
            {'name': 'Pizza', 'description': 'Authentic wood-fired pizzas with premium toppings', 'image': 'categories/Pizza.png'},
            {'name': 'Burger', 'description': 'Gourmet burgers made with fresh patties', 'image': 'categories/Burgers.png'},
            {'name': 'Pasta', 'description': 'Classic Italian pasta dishes', 'image': 'categories/Pasta.png'},
            {'name': 'Drinks', 'description': 'Refreshing beverages and cocktails', 'image': 'categories/Drinks.png'},
            {'name': 'Dessert', 'description': 'Sweet treats to end your meal', 'image': 'categories/Desserts.png'},
            {'name': 'Indian', 'description': 'Authentic Indian cuisine', 'image': 'categories/Indian.png'},
            {'name': 'Salads', 'description': 'Fresh and healthy salad bowls', 'image': 'categories/Salads.png'},
            {'name': 'Appetizers', 'description': 'Starters to kick off your meal', 'image': 'categories/Appetizers.png'},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data,
            )
            if not created:
                # Update existing categories
                for key, value in cat_data.items():
                    setattr(cat, key, value)
                cat.save()
                status = 'Updated'
            else:
                status = 'Created'
            categories[cat_data['name']] = cat
            self.stdout.write(f'  {status}: Category "{cat.name}"')

        # Create Menu Items
        items_data = [
            # Pizzas
            {
                'name': 'Margherita Pizza',
                'description': 'Classic pizza with fresh mozzarella, San Marzano tomatoes, and aromatic basil on a perfectly crispy crust.',
                'category': 'Pizza', 'price': 349, 'preparation_time': 20,
                'is_vegetarian': True, 'is_featured': True, 'calories': 850,
                'image': 'menu_items/Margherita Pizza.png',
            },
            {
                'name': 'Pepperoni Feast',
                'description': 'Loaded with spicy pepperoni, mozzarella cheese, and our signature marinara sauce.',
                'category': 'Pizza', 'price': 449, 'preparation_time': 25,
                'is_spicy': True, 'is_featured': True, 'calories': 1100,
                'image': 'menu_items/Pepperoni Feast.png',
            },
            {
                'name': 'BBQ Chicken Pizza',
                'description': 'Smoky BBQ sauce, grilled chicken, red onions, cilantro, and a blend of three cheeses.',
                'category': 'Pizza', 'price': 499, 'preparation_time': 25, 'calories': 1050,
                'image': 'menu_items/BBQ Chicken Pizza.png',
            },
            {
                'name': 'Veggie Supreme',
                'description': 'A medley of bell peppers, mushrooms, olives, onions, and fresh tomatoes on a garlic herb crust.',
                'category': 'Pizza', 'price': 399, 'preparation_time': 20,
                'is_vegetarian': True, 'calories': 780,
                'image': 'menu_items/Veggie Supreme.png',
            },

            # Burgers
            {
                'name': 'Classic Smash Burger',
                'description': 'Double smashed patties with American cheese, pickles, caramelized onions, and our special sauce.',
                'category': 'Burger', 'price': 299, 'preparation_time': 15,
                'is_featured': True, 'calories': 750,
                'image': 'menu_items/Classic Smash Burger.png',
            },
            {
                'name': 'Spicy Chicken Burger',
                'description': 'Crispy fried chicken breast with jalapeño mayo, lettuce, and pickled cucumbers.',
                'category': 'Burger', 'price': 279, 'preparation_time': 15,
                'is_spicy': True, 'calories': 680,
                'image': 'menu_items/Spicy Chicken Burger.png',
            },
            {
                'name': 'Mushroom Swiss Burger',
                'description': 'Angus beef patty topped with sautéed mushrooms and melted Swiss cheese.',
                'category': 'Burger', 'price': 349, 'preparation_time': 18, 'calories': 820,
                'image': 'menu_items/Mushroom Swiss Burger.png',
            },
            {
                'name': 'Paneer Tikka Burger',
                'description': 'Marinated paneer patty with mint chutney, crispy onions, and fresh veggies.',
                'category': 'Burger', 'price': 249, 'preparation_time': 15,
                'is_vegetarian': True, 'calories': 550,
                'image': 'menu_items/Paneer Tikka Burger.png',
            },

            # Pasta
            {
                'name': 'Creamy Alfredo Pasta',
                'description': 'Fettuccine tossed in a rich, creamy Parmesan Alfredo sauce with garlic bread.',
                'category': 'Pasta', 'price': 329, 'preparation_time': 20,
                'is_vegetarian': True, 'is_featured': True, 'calories': 890,
                'image': 'menu_items/Creamy Alfredo Pasta.png',
            },
            {
                'name': 'Penne Arrabbiata',
                'description': 'Penne pasta in a fiery tomato sauce with chili flakes, garlic, and fresh parsley.',
                'category': 'Pasta', 'price': 289, 'preparation_time': 18,
                'is_vegetarian': True, 'is_spicy': True, 'calories': 620,
                'image': 'menu_items/Penne Arrabbiata.png',
            },
            {
                'name': 'Chicken Carbonara',
                'description': 'Spaghetti with crispy chicken, egg yolk, Pecorino Romano, and black pepper cream sauce.',
                'category': 'Pasta', 'price': 379, 'preparation_time': 22, 'calories': 950,
                'image': 'menu_items/Chicken Carbonara.png',
            },

            # Indian
            {
                'name': 'Butter Chicken',
                'description': 'Tender chicken in a rich, creamy tomato-butter sauce with aromatic spices. Served with naan.',
                'category': 'Indian', 'price': 399, 'preparation_time': 30,
                'is_featured': True, 'calories': 580,
                'image': 'menu_items/Butter Chicken.png',
            },
            {
                'name': 'Paneer Butter Masala',
                'description': 'Soft paneer cubes in a luscious tomato-cashew gravy with butter and cream.',
                'category': 'Indian', 'price': 349, 'preparation_time': 25,
                'is_vegetarian': True, 'calories': 520,
                'image': 'menu_items/Paneer Butter Masala.png',
            },
            {
                'name': 'Chicken Biryani',
                'description': 'Fragrant basmati rice layered with spiced chicken, saffron, and fried onions. Served with raita.',
                'category': 'Indian', 'price': 359, 'preparation_time': 35,
                'is_spicy': True, 'is_featured': True, 'calories': 650,
                'image': 'menu_items/Chicken Biryani.png',
            },
            {
                'name': 'Dal Makhani',
                'description': 'Black lentils slow-cooked overnight with butter, cream, and aromatic spices.',
                'category': 'Indian', 'price': 249, 'preparation_time': 20,
                'is_vegetarian': True, 'calories': 380,
                'image': 'menu_items/Dal Makhani.png',
            },

            # Drinks
            {
                'name': 'Mango Lassi',
                'description': 'Creamy yogurt blended with fresh Alphonso mangoes, cardamom, and a hint of saffron.',
                'category': 'Drinks', 'price': 149, 'preparation_time': 5,
                'is_vegetarian': True, 'calories': 220,
                'image': 'menu_items/Mango Lassi.png',
            },
            {
                'name': 'Cold Brew Coffee',
                'description': 'Smooth and rich cold brew coffee, slow-steeped for 18 hours for maximum flavor.',
                'category': 'Drinks', 'price': 179, 'preparation_time': 3,
                'is_vegetarian': True, 'calories': 5,
                'image': 'menu_items/Cold Brew Coffee.png',
            },
            {
                'name': 'Fresh Lime Soda',
                'description': 'Refreshing lime juice with soda water, a pinch of salt, and fresh mint leaves.',
                'category': 'Drinks', 'price': 99, 'preparation_time': 3,
                'is_vegetarian': True, 'calories': 40,
                'image': 'menu_items/Fresh Lime Soda.png',
            },
            {
                'name': 'Berry Smoothie',
                'description': 'A blend of strawberries, blueberries, and raspberries with Greek yogurt.',
                'category': 'Drinks', 'price': 199, 'preparation_time': 5,
                'is_vegetarian': True, 'calories': 180,
                'image': 'menu_items/Berry Smoothie.png',
            },

            # Desserts
            {
                'name': 'Chocolate Lava Cake',
                'description': 'Rich, warm chocolate cake with a molten center, served with vanilla bean ice cream.',
                'category': 'Dessert', 'price': 249, 'preparation_time': 15,
                'is_vegetarian': True, 'is_featured': True, 'calories': 480,
                'image': 'menu_items/Chocolate Lava Cake.png',
            },
            {
                'name': 'Tiramisu',
                'description': 'Classic Italian dessert with espresso-soaked ladyfingers and mascarpone cream.',
                'category': 'Dessert', 'price': 299, 'preparation_time': 10,
                'is_vegetarian': True, 'calories': 420,
                'image': 'menu_items/tiramisu.png',
            },
            {
                'name': 'Gulab Jamun',
                'description': 'Soft, golden milk-solid dumplings soaked in rose-cardamom sugar syrup.',
                'category': 'Dessert', 'price': 149, 'preparation_time': 5,
                'is_vegetarian': True, 'calories': 350,
                'image': 'menu_items/gulab jamun.png',
            },

            # Salads
            {
                'name': 'Caesar Salad',
                'description': 'Crisp romaine lettuce, Parmesan, croutons, and house-made Caesar dressing.',
                'category': 'Salads', 'price': 249, 'preparation_time': 10,
                'is_vegetarian': True, 'calories': 350,
                'image': 'menu_items/cesar_salad.png',
            },
            {
                'name': 'Grilled Chicken Salad',
                'description': 'Mixed greens with grilled chicken, cherry tomatoes, avocado, and balsamic vinaigrette.',
                'category': 'Salads', 'price': 299, 'preparation_time': 12, 'calories': 420,
                'image': 'menu_items/grilled_chicken_salad.png',
            },

            # Appetizers
            {
                'name': 'Loaded Nachos',
                'description': 'Crispy tortilla chips with melted cheese, jalapeños, salsa, sour cream, and guacamole.',
                'category': 'Appetizers', 'price': 249, 'preparation_time': 12,
                'is_vegetarian': True, 'is_spicy': True, 'calories': 550,
                'image': 'menu_items/loaded_nachos.png',
            },
            {
                'name': 'Chicken Wings',
                'description': 'Crispy fried wings tossed in your choice of Buffalo, BBQ, or Honey Garlic sauce.',
                'category': 'Appetizers', 'price': 329, 'preparation_time': 15,
                'is_spicy': True, 'calories': 680,
                'image': 'menu_items/chicken_wings.png',
            },
            {
                'name': 'Spring Rolls',
                'description': 'Crispy vegetable spring rolls with sweet chili dipping sauce.',
                'category': 'Appetizers', 'price': 199, 'preparation_time': 10,
                'is_vegetarian': True, 'calories': 280,
                'image': 'menu_items/spring_rolls.png',
            },
        ]

        for item_data in items_data:
            category = categories[item_data.pop('category')]
            item, created = MenuItem.objects.get_or_create(
                name=item_data['name'],
                defaults={**item_data, 'category': category},
            )
            if not created:
                # Update existing items with their seeded values (including image)
                for key, value in item_data.items():
                    setattr(item, key, value)
                item.category = category
                item.save()
                status = 'Updated'
            else:
                status = 'Created'
            self.stdout.write(f'  {status}: "{item.name}" (Rs.{item.price})')

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! {Category.objects.count()} categories, {MenuItem.objects.count()} menu items.'
        ))
