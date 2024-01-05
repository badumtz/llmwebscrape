from dotenv import load_dotenv, find_dotenv
from scraper import scrape_restaurant_menus, scrape_cities, scrape_restaurants

load_dotenv(find_dotenv())

if __name__ == '__main__':
    # if you want to extract the cities form a tazz run the following(it's dark magic btw):
    cities_from_tazz = await scrape_cities(url="https://tazz.ro")
    # if you want to extract all the restaurants from a certain list of cities run the following(it's dark magic btw):
    city_links = ["https://tazz.ro/medias/restaurante", "https://tazz.ro/zalau/restaurante"]
    restaurants_from_certain_cities = await scrape_restaurants(city_links)
    # if you want to extract all the menu items from a certain list of restaurants run the following(it's dark magic btw):
    medias_restaurants = [{'restaurant_link': 'https://tazz.ro/medias/mia-piazzetta/10931/restaurant','restaurant_name': 'Mia Piazzetta'},
                        {'restaurant_link': 'https://tazz.ro/medias/don-giovani-pizzeria/11093/restaurant','restaurant_name': 'Don Giovani Pizzeria'}]
    restaurant_links = [restaurant['restaurant_link'] for restaurant in medias_restaurants]
    await scrape_restaurant_menus(restaurant_links)
