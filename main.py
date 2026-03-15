import asyncio
from loguru import logger

from config import Config
from utils.helpers import setup_logging, delay
from utils.exporter import DataExporter
from utils.llm_parser import LLMParser

from spiders.x5_spider import X5Spider
from spiders.magnit_spider import MagnitSpider
from spiders.yarche_spider import YarcheSpider
from spiders.kb_spider import KBSpider
from spiders.maria_ra_spider import MariaRaSpider
from spiders.chizhik_spider import ChizhikSpider


async def parse_store(spider):
    """Парсинг одного магазина"""
    try:
        await spider.parse()
        return spider.get_products()
    except Exception as e:
        logger.error(f"Ошибка при парсинге {spider.name}: {e}")
        return []


async def main():
    """Основная функция"""
    setup_logging()
    logger.info("Запуск парсера товаров")
    
    # Инициализация LLM парсера
    llm_parser = None
    if Config.USE_LLM:
        if Config.LLM_PROVIDER == 'ollama':
            # Ollama не требует API ключ
            llm_parser = LLMParser(provider=Config.LLM_PROVIDER, model=Config.OLLAMA_MODEL)
            logger.info(f"LLM парсер инициализирован: {Config.LLM_PROVIDER} (модель: {Config.OLLAMA_MODEL})")
        else:
            api_key = getattr(Config, f'{Config.LLM_PROVIDER.upper()}_API_KEY', None)
            if api_key:
                llm_parser = LLMParser(api_key=api_key, provider=Config.LLM_PROVIDER)
                logger.info(f"LLM парсер инициализирован: {Config.LLM_PROVIDER}")
            else:
                logger.warning(f"API ключ для {Config.LLM_PROVIDER} не найден. Используем традиционный парсинг.")
                Config.USE_LLM = False
    
    # Создание пауков
    spiders = [
        X5Spider(llm_parser=llm_parser),
        MagnitSpider(llm_parser=llm_parser),
        YarcheSpider(llm_parser=llm_parser),
        KBSpider(llm_parser=llm_parser),
        MariaRaSpider(llm_parser=llm_parser),
        ChizhikSpider(llm_parser=llm_parser)
    ]
    
    all_products = {}
    
    # Парсинг каждого магазина
    for spider in spiders:
        logger.info(f"Парсинг {spider.name}...")
        products = await parse_store(spider)
        all_products[spider.name] = products
        logger.info(f"Найдено {len(products)} товаров в {spider.name}")
        await delay()
    
    # Экспорт результатов
    exporter = DataExporter()
    
    # Экспорт по каждому магазину
    for store_name, products in all_products.items():
        if products:
            exporter.export_products(products, store_name)
    
    # Общий экспорт
    exporter.export_all(all_products)
    
    logger.info("Парсинг завершён")


if __name__ == '__main__':
    asyncio.run(main())
