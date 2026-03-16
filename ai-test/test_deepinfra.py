import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()


async def test_api():
    client = AsyncOpenAI(
        api_key="lOl9oQ16g9OsjPDjGbU7nLOKM9KczVKd",
        base_url="https://api.deepinfra.com/v1/openai"
    )

    try:
        response = await client.chat.completions.create(
            model="Qwen/Qwen3-Next-80B-A3B-Instruct",
            messages=[{"role": "user", "content": "Привет, мир!"}],
            max_tokens=50
        )
        print("✅ API работает!")
        print(f"Ответ: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_api())