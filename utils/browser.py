import asyncio
from playwright.async_api import async_playwright, Page, Browser
from loguru import logger
from config import Config
import random


class BrowserClient:
    """Браузер для рендеринга JavaScript сайтов"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Browser = None
        self.page: Page = None
    
    async def start(self):
        """Запустить браузер"""
        logger.info("Запуск браузера...")
        
        self.playwright = await async_playwright().start()
        
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
        
        logger.info(f"Браузер запущен (viewport: {viewport_width}x{viewport_height})")
    
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
        try:
            logger.info(f"Загрузка страницы: {url}")
            
            # Переходим на страницу
            response = await self.page.goto(url, wait_until='networkidle', timeout=60000)
            
            if response:
                logger.info(f"Статус ответа: {response.status}")
            
            # Ждём прогрузки JavaScript
            logger.info(f"Ожидание {wait_time}мс для прогрузки JS...")
            await self.page.wait_for_timeout(wait_time)
            
            # Прокручиваем страницу для загрузки ленивого контента
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self.page.wait_for_timeout(1000)
            await self.page.evaluate("window.scrollTo(0, 0)")
            await self.page.wait_for_timeout(500)
            
            # Получаем HTML
            html = await self.page.content()
            logger.info(f"HTML получен, размер: {len(html)} байт")
            
            return html
            
        except Exception as e:
            logger.error(f"Ошибка загрузки страницы {url}: {e}")
            return ""
