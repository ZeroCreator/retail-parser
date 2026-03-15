import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def get_categories():
    url = 'https://krasnoeibeloe.ru/catalog/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=30) as response:
            html = await response.text()
    
    soup = BeautifulSoup(html, 'lxml')
    
    # Ищем все ссылки
    categories = set()
    links = soup.select('a[href*="/catalog/"]')
    
    print("Найденные категории:\n")
    
    for link in links:
        href = link.get('href')
        text = link.get_text(strip=True)
        
        if href and text and '/catalog/' in href:
            # Нормализуем
            if href.startswith('/'):
                full_url = f'https://krasnoeibeloe.ru{href}'
            else:
                full_url = href
            
            # Фильтруем дубли и слишком глубокие
            if full_url.count('/') <= 5 and len(text) > 2:
                categories.add((full_url, text))
    
    # Вывод
    for url, name in sorted(categories, key=lambda x: x[1]):
        path = url.replace('https://krasnoeibeloe.ru', '')
        print(f"        '{path}',  # {name}")
    
    print(f"\nВсего: {len(categories)} категорий")

asyncio.run(get_categories())
