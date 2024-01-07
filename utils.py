import aiohttp
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")


def filter_full_restaurant_links(extracted_data, platform):
    if platform == 'tazz':
        extracted_restaurants = [restaurant for sublist in extracted_data for restaurant in sublist if
                                 '/restaurant' in restaurant['restaurant_link']]
        return extracted_restaurants
    elif platform == 'glovo':
        seen = []
        restaurants = [dict(restaurant,
                            restaurant_link='https://glovoapp.com' + restaurant['restaurant_link'] if not
                            restaurant['restaurant_link'].startswith('https://glovoapp.com') else
                            restaurant['restaurant_link']) for sublist in extracted_data for restaurant in
                       sublist if restaurant not in seen and not seen.append(restaurant) and 'restaurante_1'
                       not in restaurant['restaurant_link']]
        return restaurants[1:] if restaurants else restaurants


async def fetch_url(url, headers):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.text()


user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 11; Mobile; rv:90.0) Gecko/90.0 Firefox/90.0",
]
platforms = {
    "tazz": "https://tazz.ro",
    "glovo": "https://glovoapp.com/ro/ro/map/orase/"
}
