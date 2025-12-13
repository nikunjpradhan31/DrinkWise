from datetime import datetime
from sqlalchemy.orm import Session
from models import Drink, DrinkIngredient  # adjust import path
from database import SyncSessionLocal


drinks_data = [
    {
        "drink": {
            "name": "Espresso",
            "description": "Strong black coffee served hot",
            "category": "coffee",
            "price_tier": "$",
            "sweetness_level": 2,
            "caffeine_content": 80,
            "sugar_content": 0.0,
            "calorie_content": 5,
            "image_url": None,
            "is_alcoholic": False,
            "alcohol_content": 0.0,
            "temperature": "hot",
            "serving_size": 60.0,
            "serving_unit": "ml"
        },
        "ingredients": [
            {"ingredient_name": "Coffee Beans", "quantity": "2 tbsp", "is_allergen": False},
            {"ingredient_name": "Water", "quantity": "60 ml", "is_allergen": False}
        ]
    },
    {
        "drink": {
            "name": "Iced Latte",
            "description": "Chilled espresso with milk over ice",
            "category": "coffee",
            "price_tier": "$$",
            "sweetness_level": 5,
            "caffeine_content": 80,
            "sugar_content": 6.0,
            "calorie_content": 120,
            "image_url": None,
            "is_alcoholic": False,
            "alcohol_content": 0.0,
            "temperature": "iced",
            "serving_size": 250.0,
            "serving_unit": "ml"
        },
        "ingredients": [
            {"ingredient_name": "Espresso", "quantity": "60 ml", "is_allergen": False},
            {"ingredient_name": "Milk", "quantity": "180 ml", "is_allergen": True},
            {"ingredient_name": "Ice Cubes", "quantity": "50 g", "is_allergen": False}
        ]
    },
    {
        "drink": {
            "name": "Green Tea",
            "description": "Refreshing hot green tea",
            "category": "tea",
            "price_tier": "$",
            "sweetness_level": 3,
            "caffeine_content": 30,
            "sugar_content": 0.0,
            "calorie_content": 2,
            "image_url": None,
            "is_alcoholic": False,
            "alcohol_content": 0.0,
            "temperature": "hot",
            "serving_size": 200.0,
            "serving_unit": "ml"
        },
        "ingredients": [
            {"ingredient_name": "Green Tea Leaves", "quantity": "2 tsp", "is_allergen": False},
            {"ingredient_name": "Water", "quantity": "200 ml", "is_allergen": False}
        ]
    },
    {
        "drink": {
            "name": "Mango Smoothie",
            "description": "Sweet mango blended with yogurt and ice",
            "category": "smoothie",
            "price_tier": "$$",
            "sweetness_level": 8,
            "caffeine_content": 0,
            "sugar_content": 25.0,
            "calorie_content": 180,
            "image_url": None,
            "is_alcoholic": False,
            "alcohol_content": 0.0,
            "temperature": "cold",
            "serving_size": 300.0,
            "serving_unit": "ml"
        },
        "ingredients": [
            {"ingredient_name": "Mango", "quantity": "150 g", "is_allergen": False},
            {"ingredient_name": "Yogurt", "quantity": "100 ml", "is_allergen": True},
            {"ingredient_name": "Ice Cubes", "quantity": "50 g", "is_allergen": False}
        ]
    },
    {
        "drink": {
            "name": "Chai Latte",
            "description": "Spiced tea with milk served hot",
            "category": "tea",
            "price_tier": "$$",
            "sweetness_level": 6,
            "caffeine_content": 40,
            "sugar_content": 12.0,
            "calorie_content": 150,
            "image_url": None,
            "is_alcoholic": False,
            "alcohol_content": 0.0,
            "temperature": "hot",
            "serving_size": 250.0,
            "serving_unit": "ml"
        },
        "ingredients": [
            {"ingredient_name": "Black Tea Leaves", "quantity": "2 tsp", "is_allergen": False},
            {"ingredient_name": "Milk", "quantity": "180 ml", "is_allergen": True},
            {"ingredient_name": "Sugar", "quantity": "15 g", "is_allergen": False},
            {"ingredient_name": "Chai Spices", "quantity": "1 tsp", "is_allergen": False}
        ]
    },
    {
        "drink": {
            "name": "Mojito",
            "description": "Refreshing minty cocktail with rum",
            "category": "alcohol",
            "price_tier": "$$$",
            "sweetness_level": 6,
            "caffeine_content": 0,
            "sugar_content": 10.0,
            "calorie_content": 160,
            "image_url": None,
            "is_alcoholic": True,
            "alcohol_content": 12.0,
            "temperature": "cold",
            "serving_size": 250.0,
            "serving_unit": "ml"
        },
        "ingredients": [
            {"ingredient_name": "White Rum", "quantity": "50 ml", "is_allergen": False},
            {"ingredient_name": "Mint Leaves", "quantity": "10 g", "is_allergen": False},
            {"ingredient_name": "Sugar Syrup", "quantity": "15 ml", "is_allergen": False},
            {"ingredient_name": "Lime Juice", "quantity": "20 ml", "is_allergen": False},
            {"ingredient_name": "Soda Water", "quantity": "150 ml", "is_allergen": False}
        ]
    },
    {
        "drink": {
            "name": "Hot Chocolate",
            "description": "Rich and creamy hot cocoa",
            "category": "smoothie",
            "price_tier": "$",
            "sweetness_level": 9,
            "caffeine_content": 5,
            "sugar_content": 20.0,
            "calorie_content": 220,
            "image_url": None,
            "is_alcoholic": False,
            "alcohol_content": 0.0,
            "temperature": "hot",
            "serving_size": 250.0,
            "serving_unit": "ml"
        },
        "ingredients": [
            {"ingredient_name": "Cocoa Powder", "quantity": "2 tbsp", "is_allergen": False},
            {"ingredient_name": "Milk", "quantity": "200 ml", "is_allergen": True},
            {"ingredient_name": "Sugar", "quantity": "20 g", "is_allergen": False}
        ]
    },
    {
        "drink": {
            "name": "Cappuccino",
            "description": "Espresso with steamed milk and foam",
            "category": "coffee",
            "price_tier": "$$",
            "sweetness_level": 4,
            "caffeine_content": 80,
            "sugar_content": 5.0,
            "calorie_content": 110,
            "image_url": None,
            "is_alcoholic": False,
            "alcohol_content": 0.0,
            "temperature": "hot",
            "serving_size": 200.0,
            "serving_unit": "ml"
        },
        "ingredients": [
            {"ingredient_name": "Espresso", "quantity": "60 ml", "is_allergen": False},
            {"ingredient_name": "Steamed Milk", "quantity": "120 ml", "is_allergen": True},
            {"ingredient_name": "Milk Foam", "quantity": "20 ml", "is_allergen": True}
        ]
    },
    {
        "drink": {
            "name": "Strawberry Smoothie",
            "description": "Blended strawberries with yogurt and honey",
            "category": "smoothie",
            "price_tier": "$$",
            "sweetness_level": 7,
            "caffeine_content": 0,
            "sugar_content": 18.0,
            "calorie_content": 170,
            "image_url": None,
            "is_alcoholic": False,
            "alcohol_content": 0.0,
            "temperature": "cold",
            "serving_size": 300.0,
            "serving_unit": "ml"
        },
        "ingredients": [
            {"ingredient_name": "Strawberries", "quantity": "150 g", "is_allergen": False},
            {"ingredient_name": "Yogurt", "quantity": "100 ml", "is_allergen": True},
            {"ingredient_name": "Honey", "quantity": "20 g", "is_allergen": False},
            {"ingredient_name": "Ice Cubes", "quantity": "30 g", "is_allergen": False}
        ]
    },
    {
        "drink": {
            "name": "Whiskey Sour",
            "description": "Classic whiskey cocktail with lemon",
            "category": "alcohol",
            "price_tier": "$$$",
            "sweetness_level": 5,
            "caffeine_content": 0,
            "sugar_content": 12.0,
            "calorie_content": 180,
            "image_url": None,
            "is_alcoholic": True,
            "alcohol_content": 15.0,
            "temperature": "cold",
            "serving_size": 200.0,
            "serving_unit": "ml"
        },
        "ingredients": [
            {"ingredient_name": "Whiskey", "quantity": "50 ml", "is_allergen": False},
            {"ingredient_name": "Lemon Juice", "quantity": "25 ml", "is_allergen": False},
            {"ingredient_name": "Sugar Syrup", "quantity": "15 ml", "is_allergen": False},
            {"ingredient_name": "Egg White", "quantity": "1", "is_allergen": True}
        ]
    }
]

# Insert into database
with SyncSessionLocal() as session:
    for item in drinks_data:
        drink_info = item["drink"]
        drink = Drink(
            name=drink_info["name"],
            description=drink_info["description"],
            category=drink_info["category"],
            price_tier=drink_info["price_tier"],
            sweetness_level=drink_info["sweetness_level"],
            caffeine_content=drink_info["caffeine_content"],
            sugar_content=drink_info["sugar_content"],
            calorie_content=drink_info["calorie_content"],
            image_url=drink_info["image_url"],
            is_alcoholic=drink_info["is_alcoholic"],
            alcohol_content=drink_info["alcohol_content"],
            temperature=drink_info["temperature"],
            serving_size=drink_info["serving_size"],
            serving_unit=drink_info["serving_unit"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        for ing in item["ingredients"]:
            ingredient = DrinkIngredient(
                ingredient_name=ing["ingredient_name"],
                quantity=ing["quantity"],
                is_allergen=ing["is_allergen"]
            )
            drink.ingredients.append(ingredient)
        session.add(drink)
    session.commit()

print("10 drinks and their ingredients inserted successfully.")
