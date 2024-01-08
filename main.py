from scraper import scrape_restaurant_menus, scrape_cities, scrape_restaurants, scrape_platform

if __name__ == '__main__':

    # if you want to extract the cities from a platform(tazz or glovo) run the following(it's dark magic btw):
    cities_from_a_certain_platform = await scrape_cities(platform='')
    city_links = [city['city_link'] for city in cities_from_a_certain_platform]

    # if you want to extract all the restaurants from a certain list of cities run the following(it's dark magic btw):
    restaurants_from_certain_cities = await scrape_restaurants(city_links, platform='')
    restaurant_links = [restaurant['restaurant_link'] for restaurant in restaurants_from_certain_cities]

    # if you want to extract all the menu items from a certain list of restaurants run the following(it's dark magic btw):
    menus_from_certain_restaurants = await scrape_restaurant_menus(restaurant_links, platform='')

    # furthermore, if you want to run all of the above for a platform(tazz or glovo) run the following:
    scrape_a_certain_platform = await scrape_platform(platform='')
