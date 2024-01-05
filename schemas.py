schema_menu = {
    'properties': {
        'food_name': {
            'xpath': '//h5/text()',
            'type': 'string'
        },
        'food_price': {
            'xpath': '//span/text()',
            'type': 'string'
        },
    },
    "required": ["food_name", "food_price"],
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