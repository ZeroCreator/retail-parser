import asyncio
from typing import Optional, List
from bs4 import BeautifulSoup
from loguru import logger
import re

from spiders.base import BaseSpider
from models.product import Product
from utils.http_client import HttpClient
from utils.llm_parser import LLMParser
from utils.browser import BrowserClient
from utils.helpers import delay
from config import Config


class KBSpider(BaseSpider):
    """Парсер для Красное & Белое"""

    name = 'kb'
    base_url = 'https://krasnoeibeloe.ru'
    
    # Категории для парсинга - актуальные с сайта
    categories = [
        '/catalog/vino_import/',  # Вино импорт
        '/catalog/vino_rossiya/',  # Вино Россия
        '/catalog/vino_igristoe_vermut/',  # Игристое, вермут
        '/catalog/vodka_nastoyki/',  # Водка, настойки
        '/catalog/viski_burbon/',  # Виски, бурбон
        '/catalog/konyak_brandi/',  # Коньяк, бренди
        '/catalog/tekila_rom_liker/',  # Текила, ром, ликер
        '/catalog/pivo_import/',  # Пиво импорт
        '/catalog/pivo_rossiya/',  # Пиво Россия
        '/catalog/energetiki_kokteyli/',  # Энергетики, коктейли
        '/catalog_voda_soki_napitki/',  # Вода, соки, напитки
        '/catalog/myaso_ryba_ikra/',  # Мясо, рыба, икра
        '/catalog/zamorozka_morozhenoe/',  # Заморозка, мороженое
        '/catalog/moloko_syry_yaytso/',  # Молоко, сыры, яйцо
        '/catalog/chay_kofe/',  # Чай, кофе
        '/catalog/bakaleya_konservy/',  # Бакалея, консервы
        '/catalog/frukty_ovoshchi/',  # Фрукты, овощи
        '/catalog/shokolad_konfety/',  # Шоколад, конфеты
        '/catalog/snegi/',  # Снеки
    ]

    def __init__(self, llm_parser: LLMParser = None):
        super().__init__()
        self.http = HttpClient()
        self.llm = llm_parser
        self.browser = None

    async def parse(self):
        logger.info("=" * 80)
        logger.info(f"🍷 ЗАПУСК ПАРСЕРА КРАСНОЕ & БЕЛОЕ ({self.name})")
        logger.info("=" * 80)
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"Количество категорий: {len(self.categories)}")
        logger.info(f"USE_LLM: {Config.USE_LLM}")
        logger.info(f"USE_REMOTE_DEBUG: {Config.USE_REMOTE_DEBUG}")
        logger.info(f"REMOTE_DEBUG_PORT: {Config.REMOTE_DEBUG_PORT}")
        logger.info("=" * 80)

        # Запускаем браузер с поддержкой remote debugging если включено в конфиге
        logger.info("🌐 Инициализация BrowserClient...")
        self.browser = BrowserClient(
            use_remote_debug=Config.USE_REMOTE_DEBUG,
            remote_debug_port=Config.REMOTE_DEBUG_PORT
        )
        
        logger.info("🚀 Запуск браузера...")
        await self.browser.start()
        logger.info("✅ Браузер успешно запущен")

        try:
            if Config.USE_LLM and self.llm:
                logger.info("🤖 Парсинг с использованием LLM...")
                await self._parse_with_llm()
            else:
                logger.info("📝 Традиционный парсинг...")
                await self._parse_traditional()
        finally:
            # Закрываем браузер
            logger.info("🔒 Закрытие браузера...")
            if self.browser:
                await self.browser.close()
            logger.info("✅ Браузер закрыт")

        logger.info("=" * 80)
        logger.info(f"🎉 ЗАВЕРШЕНИЕ ПАРСИНГА {self.name}")
        logger.info(f"📦 Всего товаров собрано: {len(self.products)}")
        logger.info("=" * 80)

    async def _parse_with_llm(self):
        """Парсинг с использованием LLM"""
        logger.info("=" * 60)
        logger.info("🤖 ЗАПУСК LLM ПАРСИНГА")
        logger.info("=" * 60)
        
        for idx, category_url in enumerate(self.categories, 1):
            url = f"{self.base_url}{category_url}"
            logger.info("=" * 60)
            logger.info(f"📂 КАТЕГОРИЯ {idx}/{len(self.categories)}: {category_url}")
            logger.info(f"🔗 Полный URL: {url}")
            logger.info("=" * 60)

            try:
                # Получаем HTML через браузер с ожиданием
                logger.info(f"⏳ Загрузка HTML...")
                html = await self.browser.get_html(url, wait_time=8000)

                if not html:
                    logger.warning(f"⚠️  Пустой HTML для {category_url}")
                    continue

                logger.info(f"📄 Размер HTML: {len(html)} байт ({len(html) / 1024:.1f} KB)")

                # Сохраняем HTML для отладки
                safe_filename = category_url.replace('/', '_').strip('_')
                output_path = f'output/debug_{safe_filename}.html'
                logger.info(f"💾 Сохранение HTML для отладки: {output_path}")
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html[:50000])
                logger.info(f"✅ HTML сохранён для отладки (первые 50KB)")

                # Используем LLM для извлечения товаров
                logger.info(f"🤖 Извлечение товаров через LLM...")
                products_data = await self.llm.parse_html(html, self.name)
                logger.info(f"📦 LLM вернул {len(products_data)} товаров")

                for item in products_data:
                    product = Product(
                        name=item.get('name', ''),
                        price=float(item.get('price', 0)) if item.get('price') else 0,
                        category=category_url,
                        brand=item.get('brand'),
                        discount_price=item.get('discount_price'),
                        in_stock=item.get('in_stock', True),
                        product_url=url,
                        store=self.name
                    )
                    self.add_product(product)

                logger.info(f"✅ Обработано {len(products_data)} товаров в {category_url}")
                await delay()

            except Exception as e:
                logger.error(f"❌ Ошибка парсинга категории {category_url}: {e}")
                logger.error(f"Тип ошибки: {type(e).__name__}")
                import traceback
                logger.error(f"Stacktrace: {traceback.format_exc()}")

    async def _parse_traditional(self):
        """Традиционный парсинг через селекторы"""
        logger.info("=" * 60)
        logger.info("📝 ЗАПУСК ТРАДИЦИОННОГО ПАРСИНГА")
        logger.info("=" * 60)
        
        for idx, category_url in enumerate(self.categories, 1):
            url = f"{self.base_url}{category_url}"
            logger.info("=" * 60)
            logger.info(f"📂 КАТЕГОРИЯ {idx}/{len(self.categories)}: {category_url}")
            logger.info(f"🔗 Полный URL: {url}")
            logger.info("=" * 60)

            try:
                logger.info(f"⏳ Загрузка HTML...")
                html = await self.browser.get_html(url, wait_time=5000)
                
                if html:
                    logger.info(f"📄 HTML получен, размер: {len(html)} байт")
                    logger.info(f"🔍 Парсинг карточек товаров...")
                    await self.parse_category_from_html(html, category_url)
                else:
                    logger.warning(f"⚠️  Пустой HTML для {category_url}")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка парсинга категории {category_url}: {e}")
                logger.error(f"Тип ошибки: {type(e).__name__}")
                import traceback
                logger.error(f"Stacktrace: {traceback.format_exc()}")

            await delay()

    async def parse_category_from_html(self, html: str, category_url: str) -> list[Product]:
        """Парсинг HTML категории"""
        logger.info("🔍 Начало парсинга HTML категории...")
        products = []
        try:
            logger.info("🥣 Создание BeautifulSoup объекта...")
            soup = BeautifulSoup(html, 'lxml')
            logger.info("✅ BeautifulSoup объект создан")

            # Ищем карточки товаров
            logger.info("🔍 Поиск карточек товаров...")
            product_cards = soup.select('.goods-item, .product-item, .catalog-item, [class*="product"], [class*="goods"]')
            logger.info(f"📦 Найдено {len(product_cards)} потенциальных карточек")

            for i, card in enumerate(product_cards[:50], 1):
                logger.debug(f"  Обработка карточки {i}/{min(50, len(product_cards))}")
                product = await self._parse_card(card, category_url)
                if product:
                    products.append(product)
                    self.add_product(product)
                    logger.debug(f"    ✅ Добавлен товар: {product.name[:50]}...")

            logger.info(f"✅ Обработано {len(products)} товаров из {category_url}")

        except Exception as e:
            logger.error(f"❌ Ошибка парсинга категории {category_url}: {e}")
            logger.error(f"Тип ошибки: {type(e).__name__}")
            import traceback
            logger.error(f"Stacktrace: {traceback.format_exc()}")

        return products

    async def parse_category(self, category_url: str) -> list[Product]:
        """Парсинг страницы категории (требуется базовым классом)"""
        logger.info(f"Парсинг категории: {category_url}")
        try:
            html = await self.browser.get_html(category_url, wait_time=5000)
            if html:
                return await self.parse_category_from_html(html, category_url)
        except Exception as e:
            logger.error(f"Ошибка парсинга категории {category_url}: {e}")
        return []

    async def parse_product(self, product_url: str) -> Optional[Product]:
        """Парсинг страницы товара"""
        try:
            html = await self.http.fetch(product_url)
            soup = BeautifulSoup(html, 'lxml')

            # Извлекаем данные (селекторы нужно уточнить)
            name_el = soup.select_one('h1')
            price_el = soup.select_one('.price, .product-price, .goods-price')
            
            name = name_el.get_text(strip=True) if name_el else None
            price_text = price_el.get_text(strip=True) if price_el else None
            
            if name and price_text:
                # Очищаем цену
                price_match = re.search(r'[\d\s]+', price_text)
                if price_match:
                    price_value = float(price_match.group().replace(' ', ''))
                    return Product(
                        name=name,
                        price=price_value,
                        product_url=product_url,
                        store=self.name
                    )
        except Exception as e:
            logger.error(f"Ошибка парсинга товара {product_url}: {e}")

        return None

    async def _parse_card(self, card, category_url: str) -> Optional[Product]:
        """Парсинг карточки товара"""
        try:
            # Пробуем разные варианты селекторов
            name_el = card.select_one('.goods-name, .product-name, .item-name, [class*="name"]')
            price_el = card.select_one('.goods-price, .product-price, .item-price, .price, [class*="price"]')
            url_el = card.select_one('a[href]')
            
            name = name_el.get_text(strip=True) if name_el else None
            price_text = price_el.get_text(strip=True) if price_el else None
            url = url_el.get('href') if url_el else None

            if not name or not price_text:
                return None

            # Извлекаем число из цены
            price_match = re.search(r'[\d\s]+', price_text)
            if not price_match:
                return None
                
            price_value = float(price_match.group().replace(' ', ''))
            
            # Формируем полный URL
            if url:
                if url.startswith('/'):
                    product_url = f"{self.base_url}{url}"
                elif url.startswith('http'):
                    product_url = url
                else:
                    product_url = f"{self.base_url}/{url}"
            else:
                product_url = category_url

            return Product(
                name=name,
                price=price_value,
                product_url=product_url,
                category=category_url,
                store=self.name
            )
        except Exception as e:
            logger.error(f"Ошибка парсинга карточки: {e}")
            return None

    async def _find_subcategories(self, category_url: str) -> List[str]:
        """Найти подкатегории в категории"""
        subcategories = []
        try:
            html = await self.http.fetch(category_url)
            soup = BeautifulSoup(html, 'lxml')
            
            # Ищем ссылки на подкатегории
            links = soup.select('.subcategory a, .categories a, .nav a[href*="/catalog/"]')
            
            for link in links:
                href = link.get('href')
                if href and href.startswith('/') and '/catalog/' in href:
                    full_url = f"{self.base_url}{href}"
                    if full_url not in subcategories:
                        subcategories.append(full_url)
                        
        except Exception as e:
            logger.error(f"Ошибка поиска подкатегорий: {e}")
        
        return subcategories
