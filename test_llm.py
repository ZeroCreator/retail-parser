import asyncio
from loguru import logger

from config import Config
from utils.helpers import setup_logging
from utils.exporter import DataExporter
from utils.llm_parser import LLMParser
from models.product import Product


# Демо-HTML для тестирования (имитация ответа от магазина)
DEMO_HTML = """
<html>
<body>
<div class="catalog">
    <div class="goods-item">
        <h3 class="goods-name">Вино Красное Сухое 0.75л</h3>
        <span class="goods-price">499 ₽</span>
        <span class="goods-brand">Кубань-Вино</span>
    </div>
    <div class="goods-item">
        <h3 class="goods-name">Виски Johnnie Walker Black Label</h3>
        <span class="goods-price">1899 ₽</span>
        <span class="goods-brand">Johnnie Walker</span>
    </div>
    <div class="goods-item">
        <h3 class="goods-name">Водка Беленькая 0.5л</h3>
        <span class="goods-price">299 ₽</span>
        <span class="goods-brand">Русский Стандарт</span>
    </div>
    <div class="goods-item">
        <h3 class="goods-name">Пиво Светлое 0.5л</h3>
        <span class="goods-price">89 ₽</span>
        <span class="goods-brand">Жигулёвское</span>
    </div>
    <div class="goods-item">
        <h3 class="goods-name">Коньяк 5 звёзд 0.5л</h3>
        <span class="goods-price">799 ₽</span>
        <span class="goods-brand">Армения</span>
    </div>
</div>
</body>
</html>
"""


async def test_llm_parsing(llm_parser: LLMParser):
    """Тест парсинга с демо-HTML"""
    logger.info("Тестирование LLM парсера на демо-данных...")
    
    products_data = await llm_parser.parse_html(DEMO_HTML, 'kb_test')
    
    products = []
    for item in products_data:
        product = Product(
            name=item.get('name', ''),
            price=float(item.get('price', 0)) if item.get('price') else 0,
            category='test',
            brand=item.get('brand'),
            in_stock=item.get('in_stock', True),
            store='kb_test'
        )
        products.append(product)
    
    return products


async def main():
    """Основная функция"""
    setup_logging()
    logger.info("Тест парсера КБ с LLM (Ollama)")
    
    # Инициализация LLM парсера
    llm_parser = None
    if Config.LLM_PROVIDER == 'ollama':
        llm_parser = LLMParser(provider=Config.LLM_PROVIDER, model=Config.OLLAMA_MODEL)
        logger.info(f"LLM парсер инициализирован: {Config.LLM_PROVIDER} (модель: {Config.OLLAMA_MODEL})")
    
    # Тестируем парсинг
    products = await test_llm_parsing(llm_parser)
    
    logger.info(f"Найдено {len(products)} товаров:")
    for p in products:
        logger.info(f"  - {p.name}: {p.price} ₽ ({p.brand})")
    
    # Экспорт
    if products:
        exporter = DataExporter()
        exporter.export_products(products, 'kb_test')
        logger.info("Результаты экспортированы в output/")
    
    logger.info("Тест завершён")


if __name__ == '__main__':
    asyncio.run(main())
