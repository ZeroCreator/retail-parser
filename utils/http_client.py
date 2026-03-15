from loguru import logger
import aiohttp
from aiohttp_retry import RetryClient, ExponentialRetry
from config import Config


class HttpClient:
    """HTTP клиент для парсинга"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
    def get_retry_client(self) -> RetryClient:
        retry_options = ExponentialRetry(
            attempts=Config.RETRY_COUNT,
            statuses={500, 502, 503, 504, 429}
        )
        return RetryClient(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=Config.TIMEOUT),
            retry_options=retry_options
        )
    
    async def fetch(self, url: str) -> str:
        """Получить HTML страницы"""
        async with self.get_retry_client() as client:
            async with client.get(url) as response:
                response.raise_for_status()
                return await response.text(encoding='utf-8')
    
    async def fetch_json(self, url: str) -> dict:
        """Получить JSON"""
        async with self.get_retry_client() as client:
            async with client.get(url) as response:
                response.raise_for_status()
                return await response.json()
