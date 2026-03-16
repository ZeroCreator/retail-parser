Требуемые библиотеки:
uv add langchain langchain-community langchain-mcp-adapters

Рядом нужно запустить браузер с remote-rebugging-port
google-chrome-stable --remote-debugging-port=9222 --user-data-dir=/tmp/test google.com

```commandline
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_community.chat_models.deepinfra import ChatDeepInfra

load_dotenv()

SYSTEM_PROMPT = """
ТЫ - ПРОФЕССИОНАЛЬНЫЙ ПАРСЕР МЕДИЦИНСКИХ ЦЕН. Твоя задача - найти и собрать ВСЕ цены на медицинские услуги на данном сайте.

## СТРАТЕГИЯ ПОИСКА:
1. Сначала тщательно проанализируй главную страницу на наличие:
   - Блоков "Цены", "Прайс-лист", "Стоимость услуг"
   - Разделов с перечислением услуг (диагностика, анализы, прием специалистов)
   - Ссылок на внутренние страницы с ценами

2. ЗАТЕМ ОБЯЗАТЕЛЬНО ПЕРЕЙДИ В СЛЕДУЮЩИЕ РАЗДЕЛЫ (в порядке приоритета):
   - "Цены" / "Прайс-лист" (самый приоритетный раздел)
   - "Услуги" / "Медицинские услуги"
   - "Диагностика" / "Обследования"
   - "Лаборатория" / "Анализы"
   - "Прием специалистов" / "Врачи"
   - "Комплексные программы"
   - Разделы по специализациям: гинекология, кардиология, неврология и т.д.
   - "Цены" / "Прайс-лист" (самый приоритетный раздел)

3. ГЛУБИНА ПОИСКА:
   - Исследуй сайт до 3 уровней вглубь
   - Переходи по ВСЕМ многообещающим ссылкам в рамках лимита шагов
   - Проверяй как основное меню, так и футер сайта
   - Обращай внимание на кнопки: "Подробнее", "Записаться", "Узнать стоимость", "Цены"

## Итоговый ответ
По итогу сформируй csv файл с услугами со следующими полями: "Название услуги", "Регион", "Цена".
В качестве разделителя используй запятую. Цены указывай в рублях.
"""


async def main():
    client = MultiServerMCPClient({
        "chrome": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "chrome-devtools-mcp@latest", "--browser-url=http://127.0.0.1:9222"],
        },
    })
    agent = create_agent(
        model=ChatDeepInfra(
            model_name="meta-llama/Meta-Llama-3.1-70B-Instruct",
            deepinfra_api_key=os.getenv("OPENAI_API_KEY"),
        ),
        system_prompt=SYSTEM_PROMPT,
        tools=await client.get_tools(),
    )

    resource = "https://sun-clinic.ru/price.php"

    response = await agent.ainvoke({"messages": [{"role": "user", "content": resource}]})
    print(response)


if __name__ == "__main__":
    asyncio.run(main())

```

 deepinfra_api_key="lOl9oQ16g9OsjPDjGbU7nLOKM9KczVKd",