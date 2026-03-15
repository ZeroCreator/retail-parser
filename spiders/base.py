from abc import ABC, abstractmethod
from typing import Optional
from models.product import Product


class BaseSpider(ABC):
    """Базовый класс парсера"""
    
    name: str = 'base'
    base_url: str = ''
    
    def __init__(self):
        self.products: list[Product] = []
    
    @abstractmethod
    async def parse(self):
        """Основной метод парсинга"""
        pass
    
    @abstractmethod
    async def parse_category(self, category_url: str) -> list[Product]:
        """Парсинг категории"""
        pass
    
    @abstractmethod
    async def parse_product(self, product_url: str) -> Optional[Product]:
        """Парсинг страницы товара"""
        pass
    
    def add_product(self, product: Product):
        """Добавить товар в список"""
        self.products.append(product)
    
    def get_products(self) -> list[Product]:
        """Получить все товары"""
        return self.products
    
    def clear(self):
        """Очистить список товаров"""
        self.products = []
