import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
import re


async def main():
    print("🔧 Инициализация...")

    client = MultiServerMCPClient({
        "chrome": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "chrome-devtools-mcp@latest", "--browser-url=http://127.0.0.1:9222"],
        },
    })

    tools = await client.get_tools()
    tools_dict = {tool.name: tool for tool in tools}

    print("🚀 Начинаем сбор данных...")

    try:
        # 1. Открываем страницу
        print("📄 Открываем Яндекс.Карты...")
        await tools_dict["navigate_page"].ainvoke({
            "url": "https://yandex.ru/maps/39/rostov-na-donu/search/пиротехника/"
        })

        # 2. Ждем загрузки
        print("⏳ Ждем загрузки...")
        result = await tools_dict["wait_for"].ainvoke({
            "text": "пиротехника"
        })

        # Получаем текст
        snapshot_text = ""
        if isinstance(result, list):
            for item in result:
                if isinstance(item, dict) and "text" in item:
                    snapshot_text = item["text"]
                    break

        # Парсим данные
        print("🔍 Анализируем данные...")

        # Шаблоны для поиска магазинов
        shop_patterns = [
            r'Русский фейерверк[^"]*?"([^"]+)"[^"]*?"([^"]+)"[^"]*?"([^"]+)"',
            r'Русский Фейерверк[^"]*?"([^"]+)"[^"]*?"([^"]+)"[^"]*?"([^"]+)"',
        ]

        shops = []

        for pattern in shop_patterns:
            matches = re.finditer(pattern, snapshot_text, re.DOTALL)
            for match in matches:
                shop_data = {
                    "Название": "Русский фейерверк",
                    "Адрес": match.group(3) if len(match.groups()) >= 3 else "Не указан",
                    "Рейтинг": match.group(2) if len(match.groups()) >= 2 else "Не указан",
                    "Описание": match.group(1) if len(match.groups()) >= 1 else "Не указано"
                }
                shops.append(shop_data)

        # Выводим результаты
        print("\n" + "=" * 60)
        print("🏪 МАГАЗИНЫ ПИРОТЕХНИКИ В РОСТОВЕ-НА-ДОНУ")
        print("=" * 60)

        if shops:
            # Удаляем дубликаты
            unique_shops = []
            seen_addresses = set()

            for shop in shops:
                if shop["Адрес"] not in seen_addresses:
                    seen_addresses.add(shop["Адрес"])
                    unique_shops.append(shop)

            for i, shop in enumerate(unique_shops[:10], 1):  # Ограничиваем 10 магазинами
                print(f"\n📍 Магазин {i}:")
                print(f"   Название: {shop['Название']}")
                print(f"   Адрес: {shop['Адрес']}")
                print(f"   Рейтинг: {shop['Рейтинг']}")
                print(f"   Телефон: +7 (863) XXX-XX-XX")
                print(f"   Ссылка: https://yandex.ru/maps/org/русский_фейерверк/")
        else:
            print("❌ Не удалось найти магазины в структурированном виде")
            print("Попробуем извлечь адреса...")

            # Альтернативный поиск адресов
            address_pattern = r'(ул\.|просп\.|бульвар|шоссе|пр\.|микрорайон)[^,]+,[^"]+'
            addresses = re.findall(address_pattern, snapshot_text)

            if addresses:
                print("\n📌 Найденные адреса:")
                for addr in set(addresses[:10]):  # Уникальные адреса, не более 10
                    print(f"  - {addr}")

        # Сохраняем сырые данные
        with open("yandex_data_raw.txt", "w", encoding="utf-8") as f:
            f.write(snapshot_text)
        print(f"\n💾 Сырые данные сохранены в 'yandex_data_raw.txt'")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())