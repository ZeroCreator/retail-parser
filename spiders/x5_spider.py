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


class X5Spider(BaseSpider):
    """Парсер для X5 (Пятёрочка) с использованием LLM"""

    name = 'x5'
    base_url = 'https://5ka.ru'

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

            product_cards = soup.select('.catalog-item')

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
        try:
            html = await self.http.fetch(product_url)
            soup = BeautifulSoup(html, 'lxml')

            name_el = soup.select_one('h1.product-name')
            price_el = soup.select_one('.price-current')
            name = name_el.get_text(strip=True) if name_el else None
            price = price_el.get_text(strip=True) if price_el else None

            if name and price:
                price_value = float(price.replace('₽', '').replace(' ', ''))
                product = Product(
                    name=name,
                    price=price_value,
                    product_url=product_url,
                    store=self.name
                )
                return product
        except Exception as e:
            logger.error(f"Ошибка парсинга товара {product_url}: {e}")

        return None

    async def _parse_card(self, card) -> Optional[Product]:
        try:
            name_el = card.select_one('.item-name')
            price_el = card.select_one('.item-price')
            url_el = card.select_one('a')
            
            name = name_el.get_text(strip=True) if name_el else None
            price = price_el.get_text(strip=True) if price_el else None
            url = url_el.get('href') if url_el else None

            if not name or not price:
                return None

            price_value = float(price.replace('₽', '').replace(' ', ''))
            product_url = f"{self.base_url}{url}" if url and url.startswith('/') else url

            return Product(
                name=name,
                price=price_value,
                product_url=product_url,
                store=self.name
            )
        except Exception as e:
            logger.error(f"Ошибка парсинга карточки: {e}")
            return None
