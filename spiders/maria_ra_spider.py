import asyncio
from typing import Optional
from bs4 import BeautifulSoup
from loguru import logger

from spiders.base import BaseSpider
from models.product import Product
from utils.http_client import HttpClient
from utils.llm_parser import LLMParser
from utils.helpers import delay
from config import Config


class MariaRaSpider(BaseSpider):
    """Парсер для Мария Ра с использованием LLM"""

    name = 'maria_ra'
    base_url = 'https://maria-ra.ru'

    def __init__(self, llm_parser: LLMParser = None):
        super().__init__()
        self.http = HttpClient()
        self.llm = llm_parser

    async def parse(self):
        logger.info(f"Начало парсинга {self.name}")

        if Config.USE_LLM and self.llm:
            await self._parse_with_llm()
        else:
            await self._parse_traditional()

        logger.info(f"Завершение парсинга {self.name}: {len(self.products)} товаров")

    async def _parse_with_llm(self):
        """Парсинг с использованием LLM"""
        try:
            catalog_url = f"{self.base_url}/catalog/"
            html = await self.http.fetch(catalog_url)

            products_data = await self.llm.parse_html(html, self.name)

            for item in products_data:
                product = Product(
                    name=item.get('name', ''),
                    price=float(item.get('price', 0)),
                    category=item.get('category'),
                    brand=item.get('brand'),
                    discount_price=item.get('discount_price'),
                    in_stock=item.get('in_stock', True),
                    product_url=catalog_url,
                    store=self.name
                )
                self.add_product(product)

        except Exception as e:
            logger.error(f"Ошибка LLM парсинга {self.name}: {e}")

    async def _parse_traditional(self):
        """Традиционный парсинг через селекторы"""
        catalog_url = f"{self.base_url}/catalog/"
        await self.parse_category(catalog_url)

    async def parse_category(self, category_url: str) -> list[Product]:
        products = []
        try:
            html = await self.http.fetch(category_url)
            soup = BeautifulSoup(html, 'lxml')

            product_cards = soup.select('.product')

            for card in product_cards[:10]:
                product = await self._parse_card(card)
                if product:
                    products.append(product)
                    self.add_product(product)
                await delay()

        except Exception as e:
            logger.error(f"Ошибка парсинга категории {category_url}: {e}")

        return products

    async def parse_product(self, product_url: str) -> Optional[Product]:
        return None

    async def _parse_card(self, card) -> Optional[Product]:
        return None
