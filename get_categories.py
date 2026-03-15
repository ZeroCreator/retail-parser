import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from loguru import logger


async def get_categories():
    """Получить все категории с сайта КБ"""
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()
    
    try:
        # Переходим в каталог
        await page.goto('https://krasnoeibeloe.ru/catalog/', wait_until='networkidle')
        await page.wait_for_timeout(5000)
        
        # Прокручиваем для загрузки
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)
        
        html = await page.content()
        soup = BeautifulSoup(html, 'lxml')
        
        # Ищем все ссылки в каталоге
        logger.info("Поиск категорий...")
        
        # Пробуем разные селекторы
        selectors = [
            '.catalog-menu a',
            '.subcategory a',
            '.categories a',
            '.catalog a',
            'nav a',
            '[class*="catalog"] a',
            '[class*="menu"] a',
        ]
        
        categories = set()
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True)
                if href and '/catalog/' in href and text:
                    # Нормализуем URL
                    if href.startswith('/'):
                        full_url = f'https://krasnoeibeloe.ru{href}'
                    else:
                        full_url = href
                    
                    # Добавляем если это категория (не товар)
                    if '/catalog/' in full_url and full_url.count('/') <= 5:
                        categories.add((full_url, text))
        
        await browser.close()
        await playwright.stop()
        
        # Выводим результат
        logger.info(f"Найдено {len(categories)} категорий:\n")
        
        for url, name in sorted(categories, key=lambda x: x[1]):
            print(f"        '{url.replace('https://krasnoeibeloe.ru', '')}',  # {name}")
        
        return categories
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await browser.close()
        await playwright.stop()


if __name__ == '__main__':
    asyncio.run(get_categories())
