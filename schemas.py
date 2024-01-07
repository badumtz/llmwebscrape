schema_menu = {
    'properties': {
        "food_name": {"type": "string"},
        "food_price": {"type": "string"},
    },
    "required": ["food_name", "food_price_effective"],
}
schema_restaurant = {
    "properties": {
        "restaurant_name": {"type": "string"},
        "restaurant_link": {"type": "string"},
    },
    "required": ["restaurant_name", "restaurant_link"],
}
schema_city = {
    "properties": {
        "city_name": {"type": "string"},
        "city_link": {"type": "string"},
    },
    "required": ["city_name", "city_link"],
}