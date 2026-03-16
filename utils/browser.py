import asyncio
from playwright.async_api import async_playwright, Page, Browser
from loguru import logger
from config import Config
import random


class BrowserClient:
    """Браузер для рендеринга JavaScript сайтов"""

    def __init__(self, use_remote_debug: bool = False, remote_debug_port: int = 9222):
        """
        Инициализация браузера

        Args:
            use_remote_debug: Если True, подключаться к существующему Chrome через remote debugging
            remote_debug_port: Порт для remote debugging (по умолчанию 9222)
        """
        self.playwright = None
        self.browser: Browser = None
        self.page: Page = None
        self.use_remote_debug = use_remote_debug
        self.remote_debug_port = remote_debug_port

    async def start(self):
        """Запустить браузер"""
        logger.info("=" * 80)
        logger.info("🚀 ЗАПУСК BROWSERCLIENT")
        logger.info("=" * 80)
        logger.info(f"Режим: {'Remote Debugging' if self.use_remote_debug else 'Headless'}")
        
        self.playwright = await async_playwright().start()
        logger.info("✅ Playwright инициализирован")

        if self.use_remote_debug:
            # Подключение к существующему Chrome с remote debugging
            logger.info(f"📡 Попытка подключения к Chrome через remote debugging port {self.remote_debug_port}...")
            logger.info(f"💡 Убедитесь, что Chrome запущен с параметром:")
            logger.info(f"   google-chrome-stable --remote-debugging-port={self.remote_debug_port} --user-data-dir=/tmp/chrome-debug")
            
            # Случайная задержка перед подключением
            logger.info("⏳ Задержка перед подключением (1-3 сек)...")
            await asyncio.sleep(random.uniform(1, 3))
            
            logger.info("🔌 Выполнение подключения через CDP...")

            # Подключаемся к существующему браузеру через CDP
            try:
                self.browser = await self.playwright.chromium.connect_over_cdp(
                    f'http://localhost:{self.remote_debug_port}'
                )
                logger.info("✅ УСПЕШНОЕ ПОДКЛЮЧЕНИЕ к Chrome!")
            except Exception as e:
                logger.error(f"❌ ОШИБКА ПОДКЛЮЧЕНИЯ: {e}")
                logger.error("💡 Возможные причины:")
                logger.error("   1. Chrome не запущен с remote-debugging-port")
                logger.error("   2. Порт 9222 занят или недоступен")
                logger.error("   3. Брандмауэр блокирует подключение")
                raise

            # Используем первый существующий контекст или создаем новый
            logger.info(f"📦 Проверка контекстов браузера...")
            if self.browser.contexts:
                logger.info(f"✅ Найдено {len(self.browser.contexts)} существующих контекстов")
                context = self.browser.contexts[0]
                logger.info("📋 Используем первый существующий контекст")
            else:
                logger.info("⚠️  Контекстов не найдено, создаем новый...")
                context = await self.browser.new_context()
                logger.info("✅ Контекст создан")

            # Рандомизированный viewport
            viewport_width = random.choice([1920, 1366, 1536])
            viewport_height = random.choice([1080, 768, 864])
            
            logger.info(f"📐 Создание новой страницы с viewport {viewport_width}x{viewport_height}...")
            self.page = await context.new_page()
            await self.page.set_viewport_size({'width': viewport_width, 'height': viewport_height})
            logger.info(f"✅ Страница создана (viewport: {viewport_width}x{viewport_height})")
            
            # Проверка состояния страницы
            try:
                page_url = self.page.url
                logger.info(f"📍 Текущий URL страницы: {page_url}")
            except Exception as e:
                logger.warning(f"⚠️  Не удалось получить URL страницы: {e}")

            logger.info(f"✅ ПОДКЛЮЧЕНИЕ ЗАВЕРШЕНО (viewport: {viewport_width}x{viewport_height})")
        else:
            # Запуск нового браузера (старый режим)
            logger.info("🚀 Запуск нового Chromium браузера (headless)...")

            # Случайная задержка перед запуском
            await asyncio.sleep(random.uniform(1, 3))

            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu',
                    '--disable-blink-features=AutomationControlled'
                ]
            )

            # Рандомизированный viewport
            viewport_width = random.choice([1920, 1366, 1536])
            viewport_height = random.choice([1080, 768, 864])

            self.page = await self.browser.new_page(
                viewport={'width': viewport_width, 'height': viewport_height},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            # Скрываем признаки автоматизации
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['ru-RU', 'ru', 'en-US', 'en'],
                });
            """)

            # Блокируем лишние ресурсы для скорости
            async def intercept_route(route):
                if route.request.resource_type in ["image", "stylesheet", "font", "media"]:
                    await route.abort()
                else:
                    await route.continue_()

            await self.page.route("**/*", intercept_route)

            logger.info(f"✅ Браузер запущен (viewport: {viewport_width}x{viewport_height})")
        
        logger.info("=" * 80)
        logger.info("🎉 BROWSERCLIENT ГОТОВ К РАБОТЕ")
        logger.info("=" * 80)
    
    async def close(self):
        """Закрыть браузер"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Браузер закрыт")
        except Exception as e:
            logger.error(f"Ошибка закрытия браузера: {e}")
    
    async def get_html(self, url: str, wait_time: int = 5000) -> str:
        """
        Получить HTML страницы

        Args:
            url: URL страницы
            wait_time: Время ожидания после загрузки (мс)
        """
        logger.info("=" * 60)
        logger.info(f"🌐 ЗАГРУЗКА СТРАНИЦЫ: {url}")
        logger.info("=" * 60)
        
        try:
            # Проверка состояния страницы перед загрузкой
            logger.info("📋 Проверка состояния страницы...")
            if not self.page:
                logger.error("❌ Страница не инициализирована!")
                raise Exception("Страница не инициализирована. Вызовите start() сначала.")
            
            try:
                page_url = self.page.url
                logger.info(f"📍 Текущий URL перед загрузкой: {page_url}")
            except Exception as e:
                logger.warning(f"⚠️  Не удалось получить текущий URL: {e}")
            
            # Переходим на страницу
            logger.info(f"⏳ Выполнение goto('{url}', wait_until='networkidle')...")
            response = await self.page.goto(url, wait_until='networkidle', timeout=60000)
            
            if response:
                logger.info(f"✅ Статус ответа: {response.status}")
                logger.info(f"📍 Финальный URL: {response.url}")
            else:
                logger.warning("⚠️  Ответ не получен (None)")

            # Ждём прогрузки JavaScript
            logger.info(f"⏳ Ожидание {wait_time}мс для прогрузки JS...")
            await self.page.wait_for_timeout(wait_time)
            logger.info("✅ JS загружен")

            # Прокручиваем страницу для загрузки ленивого контента
            logger.info("📜 Прокрутка страницы для lazy loading...")
            
            logger.info("  → Прокрутка вниз...")
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self.page.wait_for_timeout(1000)
            
            logger.info("  → Прокрутка вверх...")
            await self.page.evaluate("window.scrollTo(0, 0)")
            await self.page.wait_for_timeout(500)
            
            logger.info("✅ Прокрутка завершена")

            # Получаем HTML
            logger.info("📄 Получение HTML контента...")
            html = await self.page.content()
            logger.info(f"✅ HTML получен, размер: {len(html)} байт ({len(html) / 1024:.1f} KB)")
            
            # Дополнительная информация о странице
            try:
                title = await self.page.title()
                logger.info(f"📍 Заголовок страницы: {title[:100] if title else 'N/A'}...")
            except Exception as e:
                logger.warning(f"⚠️  Не удалось получить заголовок: {e}")
            
            # Проверка на наличие элементов товаров
            try:
                product_count = await self.page.evaluate("""
                    () => {
                        const selectors = ['.goods-item', '.product-item', '.catalog-item'];
                        let count = 0;
                        selectors.forEach(sel => {
                            count += document.querySelectorAll(sel).length;
                        });
                        return count;
                    }
                """)
                logger.info(f"🛍️  Найдено элементов товаров: {product_count}")
            except Exception as e:
                logger.warning(f"⚠️  Не удалось подсчитать товары: {e}")

            return html

        except Exception as e:
            logger.error(f"❌ ОШИБКА загрузки страницы {url}: {e}")
            logger.error(f"Тип ошибки: {type(e).__name__}")
            import traceback
            logger.error(f"Stacktrace: {traceback.format_exc()}")
            return ""
