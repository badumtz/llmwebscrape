from utils import fetch_url, user_agents, platforms, llm, filter_full_restaurant_links
from lxml import html, etree
from langchain.chat_models import ChatOpenAI
from langchain.chains import create_extraction_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
import asyncio
import time
from langchain_core.documents import Document
from schemas import schema_city, schema_restaurant, schema_menu
import random
import json


def extract(content: str, schema: dict, llm: ChatOpenAI):
    return create_extraction_chain(schema=schema, llm=llm).run(content)


async def glovo_cities_main_page(platform):
    url = None
    try:
        url = platforms[platform]
        user_agent = user_agents[0]
        headers = {'User-Agent': user_agent}
        html_content = await fetch_url(url, headers)
        tree = html.fromstring(html_content)
        a_elements = tree.xpath('//body//a')
        elements = ' '.join([etree.tostring(el, encoding='unicode') for el in a_elements])
        documents = [Document(page_content=elements, metadata={"source": url})]
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=10000, chunk_overlap=0
        )
        splits = splitter.split_documents(documents)
        start_extraction = time.time()
        extracted_data = await asyncio.gather(
            *[asyncio.to_thread(extract, split.page_content, schema=schema_city, llm=llm) for split in splits])
        end_extraction = time.time()
        print(f"Time taken for LLM extraction: {end_extraction - start_extraction} seconds")
        extracted_cities = [city for sublist in extracted_data for city in sublist if
                            '/ro/ro' in city['city_link'] and 'la-domiciliu' not in city['city_link']]
        for city in extracted_cities:
            city['city_link'] = 'https://glovoapp.com' + city['city_link'] + 'restaurante_1/'
        return extracted_cities
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None


async def fetch_city_subpages_from_main_pages(city, user_agents):
    try:
        city_url = city['city_link']
        headers = {'User-Agent': user_agents}
        city_html_content = await fetch_url(city_url, headers)
        city_tree = html.fromstring(city_html_content)
        subpage_links = city_tree.xpath('//a[contains(@href, "restaurante_1/?page=")]/@href')
        city['subpage_links'] = [city['city_link']] + list(set(['https://glovoapp.com' + link for link in subpage_links]))
    except Exception as e:
        print(f"Error fetching subpages for {city['city_link']}: {e}")


async def scrape_cities(platform):
    url = None
    try:
        url = platforms[platform]
        user_agent = user_agents[0]
        headers = {'User-Agent': user_agent}
        html_content = await fetch_url(url, headers)
        tree = html.fromstring(html_content)
        a_elements = tree.xpath('//body//a')

        if platform == 'tazz':
            elements = ' '.join([etree.tostring(el, encoding='unicode') for el in a_elements])
            documents = [Document(page_content=elements, metadata={"source": url})]
            splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=10000, chunk_overlap=0
            )
            splits = splitter.split_documents(documents)
            start_extraction = time.time()
            extracted_data = await asyncio.gather(*[asyncio.to_thread(extract, split.page_content, schema=schema_city, llm=llm) for split in splits])
            end_extraction = time.time()
            print(f"Time taken for LLM extraction: {end_extraction - start_extraction} seconds")
            extracted_cities = [city for sublist in extracted_data for city in sublist if '/oras' in city['city_link']]
            for city in extracted_cities:
                city['city_link'] = city['city_link'].replace('oras', 'restaurante')
            return extracted_cities

        elif platform == 'glovo':
            unformatted_cities = await glovo_cities_main_page(platform)
            tasks = [
                fetch_city_subpages_from_main_pages(city, random.choice(user_agents))
                for city in unformatted_cities
            ]
            await asyncio.gather(*tasks)
            extracted_cities = unformatted_cities
            return extracted_cities
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None


async def scrape_restaurants_base_function(url, user_agents, platform):
    try:
        headers = {'User-Agent': user_agents}
        html_content = await fetch_url(url, headers)
        tree = html.fromstring(html_content)
        a_elements = tree.xpath('//body//a')

        elements = ' '.join([etree.tostring(el, encoding='unicode') for el in a_elements])

        documents = [Document(page_content=elements, metadata={"source": url})]

        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=10000, chunk_overlap=0
        )
        splits = splitter.split_documents(documents)

        start_extraction = time.time()
        extracted_data = await asyncio.gather(
            *[asyncio.to_thread(extract, split.page_content, schema=schema_restaurant, llm=llm) for split in
              splits])
        end_extraction = time.time()
        print(f"Time taken for LLM extraction: {end_extraction - start_extraction} seconds")
        if platform == 'tazz':
            extracted_restaurants = filter_full_restaurant_links(extracted_data, 'tazz')
            return extracted_restaurants
        elif platform == 'glovo':
            extracted_restaurants = filter_full_restaurant_links(extracted_data, 'glovo')
            return extracted_restaurants

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []


async def scrape_restaurants(urls, platform):
    tasks = [
        scrape_restaurants_base_function(url, random.choice(user_agents), platform)
        for url in urls
    ]

    results = await asyncio.gather(*tasks)
    return results


async def scrape_restaurant_menus_base_function(restaurant_link, user_agent, platform):
    try:
        headers = {'User-Agent': user_agent}
        html_content = await fetch_url(restaurant_link, headers)
        tree = html.fromstring(html_content)
        if platform == 'tazz':
            h5_elements = tree.xpath('//h5[@class="title-container"]/text()')
            span_elements = tree.xpath('//span[@class="price-container zprice"]/text()')

            elements = ' '.join(h5_elements + span_elements)

            documents = [Document(page_content=elements, metadata={"source": restaurant_link})]

            splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=10000, chunk_overlap=0
            )
            splits = splitter.split_documents(documents)

            start_extraction = time.time()
            extracted_menus = await asyncio.gather(*[asyncio.to_thread(extract, split.page_content, schema=schema_menu, llm=llm) for split in splits])
            end_extraction = time.time()
            print(f"Time taken for LLM extraction: {end_extraction - start_extraction} seconds")

            return extracted_menus
        elif platform == 'glovo':
            span_food_name_element = [el.get('text') for el in tree.xpath('//div[@class="product-row__name"]/span/span[@text]')]
            span_food_price_effective = tree.xpath('//div[@class="product-price product-row__price layout-vertical-tablet"]/span[@class="product-price__effective product-price__effective--new-card"]/text()')
            span_food_price_original = tree.xpath('//div[@class="product-price product-row__price layout-vertical-tablet"]//span[@class="product-price__original product-price__original--new-card layout-vertical-tablet"]/text()')
            if not span_food_price_original:
                span_food_price_original = span_food_price_effective
            elements = ' '.join(span_food_name_element + span_food_price_effective + span_food_price_original)

            documents = [Document(page_content=elements, metadata={"source": restaurant_link})]

            splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=10000, chunk_overlap=0
            )
            splits = splitter.split_documents(documents)

            start_extraction = time.time()
            extracted_menus = await asyncio.gather(*[asyncio.to_thread(extract, split.page_content, schema=schema_menu, llm=llm) for split in splits])
            end_extraction = time.time()
            print(f"Time taken for LLM extraction: {end_extraction - start_extraction} seconds")
            return extracted_menus
    except Exception as e:
        print(f"Error scraping {restaurant_link}: {e}")
        return None


async def scrape_restaurant_menus(urls, platform):
    tasks = [
        scrape_restaurant_menus_base_function(url, random.choice(user_agents), platform)
        for url in urls
    ]

    results = await asyncio.gather(*tasks)
    return results


async def scrape_platform(platform):
    # Scrape the cities
    cities = await scrape_cities(platform)
    with open('cities.json', 'w') as f:
        json.dump(cities, f)

    # Extract the city links
    city_links = [city['city_link'] for city in cities]

    # Scrape the restaurants
    restaurants = await scrape_restaurants(city_links, platform)
    with open('restaurants.json', 'w') as f:
        json.dump(restaurants, f)

    # Extract the restaurant links
    restaurant_links = [restaurant['restaurant_link'] for restaurant in restaurants]

    # Scrape the restaurant menus
    menus = await scrape_restaurant_menus(restaurant_links, platform)
    with open('menus.json', 'w') as f:
        json.dump(menus, f)

    # Return the menus
    return menus




