from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Product:
    """Модель товара"""
    name: str
    price: float
    currency: str = 'RUB'
    category: Optional[str] = None
    brand: Optional[str] = None
    weight: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    store: Optional[str] = None
    sku: Optional[str] = None
    discount_price: Optional[float] = None
    discount_percent: Optional[float] = None
    in_stock: bool = True
    parsed_at: datetime = None
    
    def __post_init__(self):
        if self.parsed_at is None:
            self.parsed_at = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'price': self.price,
            'currency': self.currency,
            'category': self.category,
            'brand': self.brand,
            'weight': self.weight,
            'description': self.description,
            'image_url': self.image_url,
            'product_url': self.product_url,
            'store': self.store,
            'sku': self.sku,
            'discount_price': self.discount_price,
            'discount_percent': self.discount_percent,
            'in_stock': self.in_stock,
            'parsed_at': self.parsed_at.isoformat() if self.parsed_at else None
        }
