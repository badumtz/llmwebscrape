from dotenv import load_dotenv, find_dotenv
from langchain.document_loaders import AsyncChromiumLoader
from langchain.document_transformers import BeautifulSoupTransformer
from langchain.document_loaders import AsyncHtmlLoader
from langchain.chat_models import ChatOpenAI
from langchain.chains import create_extraction_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pprint
import asyncio
from typing import List
from langchain_core.documents import Document
from itertools import cycle
import time
import random
import aiohttp

load_dotenv(find_dotenv())


async def fetch_url(url, user_agent):
    headers = {'User-Agent': user_agent}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.text()


async def scrape_city_restaurants(city_link, schema_restaurant):
    user_agent = next(user_agent_cycle)
    loader = AsyncChromiumLoader([city_link])
    html = await loader.ascrape_playwright(city_link)
    document = Document(page_content=html, metadata={"source": city_link})

    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents([document], tags_to_extract=["a"])
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=10000, chunk_overlap=0
    )
    splits = splitter.split_documents([docs_transformed[0]])
    extracted_content = [extract(split.page_content, schema=schema_restaurant) for split in splits]

    return extracted_content


def extract(content: str, schema: dict):
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")
    return create_extraction_chain(schema=schema, llm=llm).run(content)


def scrape_with_playwright(urls, schema):
    loader = AsyncChromiumLoader(urls)
    html = loader.load()
    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(html, tags_to_extract=["a"])
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=10000, chunk_overlap=0)
    splits = splitter.split_documents(docs_transformed)
    extracted_content = [extract(split.page_content, schema=schema) for split in splits]
    return extracted_content


if __name__ == '__main__':
    extracted_cities = [{'city_name': 'Timișoara', 'city_link': 'https://tazz.ro/timisoara/restaurante'},
                        {'city_name': 'Cluj-Napoca', 'city_link': 'https://tazz.ro/cluj-napoca/restaurante'},
                        {'city_name': 'București', 'city_link': 'https://tazz.ro/bucuresti/restaurante'},
                        {'city_name': 'Iași', 'city_link': 'https://tazz.ro/iasi/restaurante'},
                        {'city_name': 'Arad', 'city_link': 'https://tazz.ro/arad/restaurante'},
                        {'city_name': 'Brașov', 'city_link': 'https://tazz.ro/brasov/restaurante'},
                        {'city_name': 'Oradea', 'city_link': 'https://tazz.ro/oradea/restaurante'},
                        {'city_name': 'Sibiu', 'city_link': 'https://tazz.ro/sibiu/restaurante'},
                        {'city_name': 'Deva', 'city_link': 'https://tazz.ro/deva/restaurante'},
                        {'city_name': 'Alba Iulia', 'city_link': 'https://tazz.ro/alba-iulia/restaurante'},
                        {'city_name': 'Baia Mare', 'city_link': 'https://tazz.ro/baia-mare/restaurante'},
                        {'city_name': 'Ploiești', 'city_link': 'https://tazz.ro/ploiesti/restaurante'},
                        {'city_name': 'Craiova', 'city_link': 'https://tazz.ro/craiova/restaurante'},
                        {'city_name': 'Brăila', 'city_link': 'https://tazz.ro/braila/restaurante'},
                        {'city_name': 'Reșița', 'city_link': 'https://tazz.ro/resita/restaurante'},
                        {'city_name': 'Botoșani', 'city_link': 'https://tazz.ro/botosani/restaurante'},
                        {'city_name': 'Pitești', 'city_link': 'https://tazz.ro/pitesti/restaurante'},
                        {'city_name': 'Târgu Mureș', 'city_link': 'https://tazz.ro/targu-mures/restaurante'},
                        {'city_name': 'Constanța', 'city_link': 'https://tazz.ro/constanta/restaurante'},
                        {'city_name': 'Suceava', 'city_link': 'https://tazz.ro/suceava/restaurante'},
                        {'city_name': 'Galați', 'city_link': 'https://tazz.ro/galati/restaurante'},
                        {'city_name': 'Râmnicu Vâlcea', 'city_link': 'https://tazz.ro/ramnicu-valcea/restaurante'},
                        {'city_name': 'Bacău', 'city_link': 'https://tazz.ro/bacau/restaurante'},
                        {'city_name': 'Târgu Jiu', 'city_link': 'https://tazz.ro/targu-jiu/restaurante'},
                        {'city_name': 'Drobeta-Turnu Severin', 'city_link': 'https://tazz.ro/drobeta-turnu-severin/restaurante'},
                        {'city_name': 'Buzău', 'city_link': 'https://tazz.ro/buzau/restaurante'},
                        {'city_name': 'Slatina', 'city_link': 'https://tazz.ro/slatina/restaurante'},
                        {'city_name': 'Zalǎu', 'city_link': 'https://tazz.ro/zalau/restaurante'},
                        {'city_name': 'Mediaș', 'city_link': 'https://tazz.ro/medias/restaurante'},
                        {'city_name': 'Otopeni-Corbeanca', 'city_link': 'https://tazz.ro/otopeni-corbeanca/restaurante'},
                        {'city_name': 'Focșani', 'city_link': 'https://tazz.ro/focsani/restaurante'},
                        {'city_name': 'Târgoviște', 'city_link': 'https://tazz.ro/targoviste/restaurante'},
                        {'city_name': 'Petroșani', 'city_link': 'https://tazz.ro/petrosani/restaurante'},
                        {'city_name': 'Sfântu Gheorghe', 'city_link': 'https://tazz.ro/sfantu-gheorghe/restaurante'},
                        {'city_name': 'Piatra Neamț', 'city_link': 'https://tazz.ro/piatra-neamt/restaurante'},
                        {'city_name': 'Vaslui', 'city_link': 'https://tazz.ro/vaslui/restaurante'}]
    city_links = ['https://tazz.ro/medias/restaurante', 'https://tazz.ro/cluj-napoca/restaurante', 'https://tazz.ro/bucuresti/restaurante', 'https://tazz.ro/iasi/restaurante', 'https://tazz.ro/arad/restaurante', 'https://tazz.ro/brasov/restaurante', 'https://tazz.ro/oradea/restaurante', 'https://tazz.ro/sibiu/restaurante', 'https://tazz.ro/deva/restaurante', 'https://tazz.ro/alba-iulia/restaurante', 'https://tazz.ro/baia-mare/restaurante', 'https://tazz.ro/ploiesti/restaurante', 'https://tazz.ro/craiova/restaurante', 'https://tazz.ro/braila/restaurante', 'https://tazz.ro/resita/restaurante', 'https://tazz.ro/botosani/restaurante', 'https://tazz.ro/pitesti/restaurante', 'https://tazz.ro/targu-mures/restaurante', 'https://tazz.ro/constanta/restaurante', 'https://tazz.ro/suceava/restaurante', 'https://tazz.ro/galati/restaurante', 'https://tazz.ro/ramnicu-valcea/restaurante', 'https://tazz.ro/bacau/restaurante', 'https://tazz.ro/targu-jiu/restaurante', 'https://tazz.ro/drobeta-turnu-severin/restaurante', 'https://tazz.ro/buzau/restaurante', 'https://tazz.ro/slatina/restaurante', 'https://tazz.ro/zalau/restaurante', 'https://tazz.ro/timisoara/restaurante', 'https://tazz.ro/otopeni-corbeanca/restaurante', 'https://tazz.ro/focsani/restaurante', 'https://tazz.ro/targoviste/restaurante', 'https://tazz.ro/petrosani/restaurante', 'https://tazz.ro/sfantu-gheorghe/restaurante', 'https://tazz.ro/piatra-neamt/restaurante', 'https://tazz.ro/vaslui/restaurante']

    schema_restaurant = {
        "properties": {
            "restaurant_name": {"type": "string"},
            "restaurant_link": {"type": "string"},
        },
        "required": ["restaurant_name", "restaurant_link"],
    }
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
    user_agent_cycle = cycle(user_agents)
    city_link_to_test = 'https://tazz.ro/medias/restaurante'
    result = asyncio.run(scrape_city_restaurants(city_link_to_test, schema_restaurant))


