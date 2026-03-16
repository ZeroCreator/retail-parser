"""
Тест подключения к Chrome Remote Debugging
Запустите этот скрипт для проверки, что Chrome доступен через remote debugging
"""

import asyncio
from playwright.async_api import async_playwright
import urllib.request
import json


def check_chrome_debug_port(port=9222):
    """Проверка, доступен ли порт Chrome DevTools"""
    url = f'http://localhost:{port}/json'
    print(f"🔍 Проверка порта {port}...")
    print(f"   URL: {url}")
    
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            print(f"✅ Chrome DevTools доступен!")
            print(f"   Найдено вкладок: {len(data)}")
            
            if data:
                print("\n   Активные вкладки:")
                for i, tab in enumerate(data[:5], 1):
                    print(f"      {i}. {tab.get('title', 'N/A')[:60]}")
                    print(f"       URL: {tab.get('url', 'N/A')[:60]}")
            
            return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n💡 Возможные причины:")
        print("   1. Chrome не запущен с --remote-debugging-port=9222")
        print("   2. Порт 9222 занят другим процессом")
        print("   3. Брандмауэр блокирует подключение")
        return False


async def test_connection(port=9222):
    """Тест подключения через Playwright"""
    print("\n" + "=" * 80)
    print("📡 ТЕСТ ПОДКЛЮЧЕНИЯ ЧЕРЕЗ PLAYWRIGHT")
    print("=" * 80)
    
    async with async_playwright() as p:
        try:
            print(f"\n🔌 Подключение к localhost:{port}...")
            browser = await p.chromium.connect_over_cdp(f'http://localhost:{port}')
            print("✅ УСПЕШНОЕ ПОДКЛЮЧЕНИЕ!")
            
            print(f"\n📦 Контекстов браузера: {len(browser.contexts)}")
            
            if browser.contexts:
                context = browser.contexts[0]
                print(f"   Используем существующий контекст")
                print(f"   Страниц в контексте: {len(context.pages)}")
            else:
                print("   Создаем новый контекст...")
                context = await browser.new_context()
                print("   ✅ Контекст создан")
            
            # Создаем тестовую страницу
            print("\n📐 Создание тестовой страницы...")
            page = await context.new_page()
            print("   ✅ Страница создана")
            
            # Переходим на тестовую страницу
            print("\n🌐 Переход на google.com...")
            response = await page.goto('https://google.com', wait_until='networkidle')
            print(f"   ✅ Статус: {response.status}")
            
            # Получаем заголовок
            title = await page.title()
            print(f"   📍 Заголовок: {title}")
            
            # Делаем скриншот
            print("\n📸 Создание скриншота...")
            await page.screenshot(path='output/test_remote_debug.png')
            print("   ✅ Скриншот сохранен: output/test_remote_debug.png")
            
            # Закрываем страницу
            await page.close()
            print("\n✅ Тест успешно завершен!")
            
        except Exception as e:
            print(f"\n❌ ОШИБКА ПОДКЛЮЧЕНИЯ: {e}")
            print("\n💡 Решение:")
            print("   1. Убедитесь, что Chrome запущен с правильными параметрами")
            print("   2. Проверьте порт: lsof -i :9222")
            print("   3. Перезапустите Chrome")
            import traceback
            traceback.print_exc()


async def main():
    print("=" * 80)
    print("🧪 ТЕСТИРОВАНИЕ CHROME REMOTE DEBUGGING")
    print("=" * 80)
    
    # Создаем папку для результатов
    import os
    os.makedirs('output', exist_ok=True)
    
    # Проверка порта
    print("\n" + "=" * 80)
    print("🔍 ПРОВЕРКА ЧЕРЕЗ DEVTOOLS API")
    print("=" * 80)
    
    is_available = check_chrome_debug_port(9222)
    
    if is_available:
        # Тест подключения через Playwright
        await test_connection(9222)
    else:
        print("\n" + "=" * 80)
        print("⚠️  Chrome Remote Debugging НЕ ДОСТУПЕН")
        print("=" * 80)
        print("\n📋 Инструкция по запуску:")
        print("   1. Закройте все экземпляры Chrome")
        print("   2. Запустите команду:")
        print("      google-chrome-stable --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug")
        print("   3. Убедитесь, что браузер открылся")
        print("   4. Запустите этот скрипт повторно")


if __name__ == '__main__':
    asyncio.run(main())
