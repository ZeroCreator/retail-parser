import asyncio
import json
from loguru import logger
from utils.http_client import HttpClient
from config import Config


class LLMParser:
    """Парсер с использованием LLM для извлечения данных"""
    
    def __init__(self, api_key: str = None, provider: str = "ollama", model: str = None):
        self.api_key = api_key or "ollama"  # Ollama не требует ключ
        self.provider = provider
        self.model = model
        self.http = HttpClient()
        
        # Поддержка разных провайдеров
        self.providers = {
            "ollama": {
                "url": "http://localhost:11434/api/generate",
                "model": model or "qwen2.5:7b",
                "headers": lambda key: {
                    "Content-Type": "application/json"
                }
            },
            "openai": {
                "url": "https://api.openai.com/v1/chat/completions",
                "model": "gpt-4o-mini",
                "headers": lambda key: {
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                }
            },
            "anthropic": {
                "url": "https://api.anthropic.com/v1/messages",
                "model": "claude-sonnet-4-20250514",
                "headers": lambda key: {
                    "x-api-key": key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                }
            },
            "dashscope": {
                "url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                "model": "qwen-plus",
                "headers": lambda key: {
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                }
            },
            "huggingface": {
                "url": "https://api-inference.huggingface.co/models",
                "model": "Qwen/Qwen2.5-72B-Instruct",
                "headers": lambda key: {
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                }
            },
            "groq": {
                "url": "https://api.groq.com/openai/v1/chat/completions",
                "model": "llama-3.3-70b-versatile",
                "headers": lambda key: {
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                }
            },
            "google": {
                "url": "https://generativelanguage.googleapis.com/v1beta/models",
                "model": "gemini-1.5-flash",
                "headers": lambda key: {
                    "Content-Type": "application/json"
                }
            }
        }
    
    async def parse_html(self, html: str, store_name: str) -> list[dict]:
        """Извлечь товары из HTML с помощью LLM"""
        
        prompt = f"""Ты парсер товаров интернет-магазина {store_name}.
Извлеки все товары из HTML и верни строго JSON массив.

Для каждого товара извлеки:
- name: название товара
- price: цена (число, без символа валюты)
- category: категория (если есть)
- brand: бренд (если есть)
- discount_price: цена со скидкой (если есть)
- in_stock: есть ли в наличии (true/false)

Если товар не имеет цены или названия - пропусти его.

Верни ТОЛЬКО JSON массив в формате:
[
  {{"name": "Товар 1", "price": 100, "category": "Молоко", "in_stock": true}},
  {{"name": "Товар 2", "price": 250.50, "in_stock": true}}
]

HTML для анализа:
{html[:30000]}
"""
        
        try:
            if self.provider == "ollama":
                response = await self._call_ollama(prompt)
            elif self.provider == "anthropic":
                response = await self._call_anthropic(prompt)
            elif self.provider == "dashscope":
                response = await self._call_dashscope(prompt)
            elif self.provider == "groq":
                response = await self._call_groq(prompt)
            elif self.provider == "google":
                response = await self._call_google(prompt)
            elif self.provider == "huggingface":
                response = await self._call_huggingface(prompt)
            else:
                response = await self._call_openai(prompt)
            
            products = self._parse_response(response)
            logger.info(f"LLM извлек {len(products)} товаров из {store_name}")
            return products
            
        except Exception as e:
            logger.error(f"Ошибка LLM парсинга {store_name}: {e}")
            return []
    
    async def _call_ollama(self, prompt: str) -> str:
        """Вызов локальной Ollama"""
        import aiohttp
        
        payload = {
            "model": self.providers["ollama"]["model"],
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 2048
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.providers["ollama"]["url"],
                headers=self.providers["ollama"]["headers"](self.api_key),
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                data = await response.json()
                return data.get("response", "")
    
    async def _call_openai(self, prompt: str) -> str:
        """Вызов OpenAI API"""
        import aiohttp
        
        payload = {
            "model": self.providers["openai"]["model"],
            "messages": [
                {"role": "system", "content": "You are a JSON-only assistant. Return ONLY valid JSON array."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.providers["openai"]["url"],
                headers=self.providers["openai"]["headers"](self.api_key),
                json=payload
            ) as response:
                data = await response.json()
                return data["choices"][0]["message"]["content"]
    
    async def _call_anthropic(self, prompt: str) -> str:
        """Вызов Anthropic API"""
        import aiohttp

        payload = {
            "model": self.providers["anthropic"]["model"],
            "max_tokens": 4096,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.providers["anthropic"]["url"],
                headers=self.providers["anthropic"]["headers"](self.api_key),
                json=payload
            ) as response:
                data = await response.json()
                return data["content"][0]["text"]
    
    async def _call_dashscope(self, prompt: str) -> str:
        """Вызов DashScope (Qwen) API"""
        import aiohttp
        
        payload = {
            "model": self.providers["dashscope"]["model"],
            "input": {
                "messages": [
                    {"role": "system", "content": "You are a JSON-only assistant. Return ONLY valid JSON array."},
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "result_format": "message"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.providers["dashscope"]["url"],
                headers=self.providers["dashscope"]["headers"](self.api_key),
                json=payload
            ) as response:
                data = await response.json()
                return data["output"]["choices"][0]["message"]["content"]

    async def _call_google(self, prompt: str) -> str:
        """Вызов Google AI (Gemini) API"""
        import aiohttp
        
        url = f"{self.providers['google']['url']}/{self.providers['google']['model']}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0,
                "responseMimeType": "application/json"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=self.providers["google"]["headers"](self.api_key),
                json=payload
            ) as response:
                data = await response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
    
    async def _call_groq(self, prompt: str) -> str:
        """Вызов Groq API"""
        import aiohttp
        
        payload = {
            "model": self.providers["groq"]["model"],
            "messages": [
                {"role": "system", "content": "You are a JSON-only assistant. Return ONLY valid JSON array."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.providers["groq"]["url"],
                headers=self.providers["groq"]["headers"](self.api_key),
                json=payload
            ) as response:
                data = await response.json()
                return data["choices"][0]["message"]["content"]

    async def _call_huggingface(self, prompt: str) -> str:
        """Вызов Hugging Face Inference API"""
        import aiohttp
        
        model = self.providers["huggingface"]["model"]
        url = f"{self.providers['huggingface']['url']}/{model}"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 2048,
                "temperature": 0.1,
                "return_full_text": False
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=self.providers["huggingface"]["headers"](self.api_key),
                json=payload
            ) as response:
                data = await response.json()
                # HF возвращает список с генерацией
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get("generated_text", "")
                elif isinstance(data, dict):
                    return data.get("generated_text", "")
                return str(data)
    
    def _parse_response(self, response: str) -> list[dict]:
        """Распарсить JSON ответ от LLM"""
        try:
            # Очистка от markdown обёрток
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            data = json.loads(response.strip())
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "products" in data:
                return data["products"]
            else:
                logger.warning(f"Неожиданный формат JSON: {type(data)}")
                return []
                
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON от LLM: {e}")
            logger.debug(f"Raw response: {response[:500]}")
            return []
