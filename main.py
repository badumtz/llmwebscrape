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

load_dotenv(find_dotenv())


async def scrape_city_restaurants(city_link, schema_restaurant):
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


def scrape_restaurants(urls_cities, schema_restaurant):
    """Scrape restaurant links from all city pages."""
    all_restaurants = []
    for city_link in urls_cities:
        restaurants = asyncio.run(scrape_city_restaurants(city_link, schema_restaurant))
        all_restaurants.append(restaurants)
    return all_restaurants


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
    urls_cities = ["https://tazz.ro"]

    schema_city = {
        "properties": {
            "city_name": {"type": "string"},
            "city_link": {"type": "string"},

        },
        "required": ["city_link", "city_name"],
    }
    extracted_cities = scrape_with_playwright(urls_cities, schema_city)
    zalau_link = ["https://tazz.ro/zalau/restaurante"]
    schema_restaurant = {
        "properties": {
            "restaurant_name": {"type": "string"},
            "restaurant_link": {"type": "string"},
        },
        "required": ["restaurant_name", "restaurant_link"],
    }

    async def main():
        for city_info in extracted_cities:
            extracted_restaurants = await scrape_city_restaurants(city_info["https://tazz.ro/zalau/restaurante"], schema_restaurant)
            pprint.pprint(extracted_restaurants)
    asyncio.run(main())
