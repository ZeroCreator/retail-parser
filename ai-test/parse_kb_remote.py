"""
Парсер Красное & Белое с использованием Remote Debugging
Версия с подробным логированием для отладки

ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ:
1. Запустите Chrome с remote debugging:
   google-chrome-stable --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug

2. Убедитесь, что браузер запущен и доступен на порту 9222

3. Установите зависимости:
   pip install playwright
   playwright install
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
import re
import os


async def parse_krasnoe_beloe_remote():
    """Парсер КБ с подключением к существующему Chrome через remote debugging"""
    
    print("=" * 80)
    print("🛒 ПАРСЕР КРАСНОЕ & БЕЛОЕ (Remote Debugging)")
    print("=" * 80)
    
    # URL для парсинга
    base_url = "https://krasnoeibeloe.ru"
    test_categories = [
        "/catalog/vino_import/",
        "/catalog/vodka_nastoyki/",
    ]
    
    async with async_playwright() as p:
        # ПОДКЛЮЧАЕМСЯ К СУЩЕСТВУЮЩЕМУ БРАУЗЕРУ
        print("\n" + "=" * 80)
        print("📡 ПОДКЛЮЧЕНИЕ К CHROME")
        print("=" * 80)
        print("\n📡 Подключение к Chrome через remote debugging port 9222...")
        print("💡 Убедитесь, что Chrome запущен с параметром:")
        print("   google-chrome-stable --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug")
        
        try:
            print("🔌 Выполнение подключения...")
            browser = await p.chromium.connect_over_cdp('http://localhost:9222')
            print("✅ УСПЕШНОЕ ПОДКЛЮЧЕНИЕ к Chrome!")
        except Exception as e:
            print(f"\n❌ ОШИБКА ПОДКЛЮЧЕНИЯ: {e}")
            print("\n🔧 Решение:")
            print("1. Запустите Chrome с remote debugging портом")
            print("2. Проверьте, что порт 9222 не занят: lsof -i :9222")
            print("3. Убедитесь, что Chrome полностью загрузился")
            print("4. Проверьте, что Chrome виден по адресу: http://localhost:9222/json")
            return
        
        # Используем первый контекст или создаем новый
        print("\n📦 Проверка контекстов браузера...")
        if browser.contexts:
            print(f"✅ Найдено {len(browser.contexts)} существующих контекстов")
            context = browser.contexts[0]
            print("📋 Используем первый существующий контекст")
        else:
            print("⚠️  Контекстов не найдено, создаем новый...")
            context = await browser.new_context()
            print("✅ Контекст создан")
        
        # Создаем новую страницу
        print("\n📐 Создание новой страницы...")
        page = await context.new_page()
        await page.set_viewport_size({'width': 1920, 'height': 1080})
        print("✅ Страница создана (viewport: 1920x1080)")
        
        # Проверка состояния
        try:
            page_url = page.url
            print(f"📍 Текущий URL страницы: {page_url}")
        except Exception as e:
            print(f"⚠️  Не удалось получить URL: {e}")
        
        all_products = []
        
        # Парсим каждую категорию
        for idx, category_url in enumerate(test_categories, 1):
            print("\n" + "=" * 80)
            print(f"📂 КАТЕГОРИЯ {idx}/{len(test_categories)}")
            print("=" * 80)
            
            url = f"{base_url}{category_url}"
            print(f"🔗 URL: {url}")
            print("=" * 80)
            
            try:
                # Переходим на страницу
                print("\n🌐 ШАГ 1: Переход на страницу...")
                print("   Выполнение: page.goto(url, wait_until='networkidle')")
                response = await page.goto(url, wait_until='networkidle', timeout=60000)
                
                if response:
                    print(f"   ✅ Статус ответа: {response.status}")
                    print(f"   📍 Финальный URL: {response.url}")
                else:
                    print("   ⚠️  Ответ не получен")
                
                # Ждем прогрузки JavaScript
                print("\n🌐 ШАГ 2: Ожидание загрузки JavaScript...")
                print("   Выполнение: wait_for_timeout(5000)")
                await page.wait_for_timeout(5000)
                print("   ✅ JS загружен")
                
                # Прокручиваем страницу для lazy loading
                print("\n🌐 ШАГ 3: Прокрутка для lazy loading...")
                print("   → Прокрутка вниз...")
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(2000)
                
                print("   → Прокрутка вверх...")
                await page.evaluate("window.scrollTo(0, 0)")
                await page.wait_for_timeout(1000)
                print("   ✅ Прокрутка завершена")
                
                # Получаем HTML
                print("\n🌐 ШАГ 4: Получение HTML контента...")
                html = await page.content()
                print(f"   ✅ HTML получен, размер: {len(html)} байт ({len(html) / 1024:.1f} KB)")
                
                # Дополнительная информация
                try:
                    title = await page.title()
                    print(f"   📍 Заголовок страницы: {title[:100] if title else 'N/A'}")
                except Exception as e:
                    print(f"   ⚠️  Не удалось получить заголовок: {e}")
                
                # Проверка на наличие элементов товаров
                try:
                    product_count = await page.evaluate("""
                        () => {
                            const selectors = ['.goods-item', '.product-item', '.catalog-item'];
                            let count = 0;
                            selectors.forEach(sel => {
                                count += document.querySelectorAll(sel).length;
                            });
                            return count;
                        }
                    """)
                    print(f"   🛍️  Найдено элементов товаров на странице: {product_count}")
                except Exception as e:
                    print(f"   ⚠️  Не удалось подсчитать товары: {e}")
                
                # Сохраняем HTML для отладки
                print("\n💾 ШАГ 5: Сохранение HTML для отладки...")
                os.makedirs('output', exist_ok=True)
                safe_filename = category_url.replace('/', '_').strip('_')
                output_path = f'output/kb_debug{safe_filename}.html'
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html[:50000])
                print(f"   ✅ HTML сохранен: {output_path} (первые 50KB)")
                
                # Парсим HTML через BeautifulSoup
                print("\n🔍 ШАГ 6: Парсинг HTML через BeautifulSoup...")
                products = parse_products_from_html(html, category_url, base_url)
                
                print(f"\n📊 РЕЗУЛЬТАТЫ КАТЕГОРИИ")
                print(f"   🛍️  Найдено товаров: {len(products)}")
                
                # Показываем первые несколько товаров
                if products:
                    print("\n   📋 Примеры товаров:")
                    for i, product in enumerate(products[:5], 1):
                        print(f"      {i}. {product['name']} - {product['price']} ₽")
                
                all_products.extend(products)
                
                print("\n⏳ Задержка перед следующей категорией (2 сек)...")
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"\n❌ ОШИБКА парсинга категории {category_url}: {e}")
                print(f"   Тип ошибки: {type(e).__name__}")
                import traceback
                print(f"   Stacktrace:")
                traceback.print_exc()
        
        # ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ
        print("\n" + "=" * 80)
        print("📊 ОБЩИЕ РЕЗУЛЬТАТЫ")
        print("=" * 80)
        print(f"📦 Всего товаров найдено: {len(all_products)}")
        
        if all_products:
            # Сохраняем результаты в JSON
            os.makedirs('output', exist_ok=True)
            output_file = 'output/kb_remote_debug_products.json'
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_products, f, ensure_ascii=False, indent=2)
            print(f"💾 Результаты сохранены: {output_file}")
            
            # Показываем все товары
            print(f"\n📋 ВСЕ ТОВАРЫ ({len(all_products)} шт):")
            for i, product in enumerate(all_products, 1):
                print(f"   {i:3d}. {product['name'][:60]} - {product['price']:>7.0f} ₽")
        
        # Закрываем только страницу, браузер остается работать
        print("\n🔒 Закрытие страницы...")
        await page.close()
        print("✅ Страница закрыта")
        print("\n💡 Chrome продолжает работать")
        print("   Вы можете продолжить использовать браузер для других задач")
        
        print("\n" + "=" * 80)
        print("🎉 ПАРСИНГ ЗАВЕРШЕН")
        print("=" * 80)


def parse_products_from_html(html: str, category_url: str, base_url: str) -> list:
    """Парсинг товаров из HTML"""
    products = []
    
    soup = BeautifulSoup(html, 'lxml')
    
    # Ищем карточки товаров по разным селекторам
    selectors = [
        '.goods-item',
        '.product-item', 
        '.catalog-item',
        '[class*="product"]',
        '[class*="goods"]'
    ]
    
    print("   🔍 Поиск карточек товаров...")
    product_cards = []
    for selector in selectors:
        cards = soup.select(selector)
        if cards:
            print(f"      ✅ Найдено {len(cards)} элементов с селектором '{selector}'")
            product_cards.extend(cards[:20])  # Берем первые 20
    
    # Убираем дубликаты
    seen = set()
    unique_cards = []
    for card in product_cards:
        card_hash = hash(str(card))
        if card_hash not in seen:
            seen.add(card_hash)
            unique_cards.append(card)
    
    print(f"   📦 Уникальных карточек: {len(unique_cards)}")
    
    for card in unique_cards:
        product = extract_product(card, category_url, base_url)
        if product and product['name'] and product['price']:
            products.append(product)
    
    return products


def extract_product(card, category_url: str, base_url: str) -> dict:
    """Извлечение данных из карточки товара"""
    try:
        # Название
        name_el = card.select_one('.goods-name, .product-name, .item-name, [class*="name"]')
        name = name_el.get_text(strip=True) if name_el else None
        
        # Цена
        price_el = card.select_one('.goods-price, .product-price, .item-price, .price, [class*="price"]')
        price_text = price_el.get_text(strip=True) if price_el else None
        
        # Ссылка
        url_el = card.select_one('a[href]')
        url = url_el.get('href') if url_el else None
        
        if not name or not price_text:
            return None
        
        # Извлекаем число из цены
        price_match = re.search(r'[\d\s]+', price_text)
        if not price_match:
            return None
        
        price_value = float(price_match.group().replace(' ', ''))
        
        # Формируем полный URL
        if url:
            if url.startswith('/'):
                product_url = f"{base_url}{url}"
            elif url.startswith('http'):
                product_url = url
            else:
                product_url = f"{base_url}/{url}"
        else:
            product_url = f"{base_url}{category_url}"
        
        return {
            'name': name,
            'price': price_value,
            'category': category_url,
            'product_url': product_url,
            'store': 'kb'
        }
        
    except Exception as e:
        print(f"   ⚠️  Ошибка извлечения товара: {e}")
        return None


async def main():
    """Точка входа"""
    # Создаем папку для вывода
    os.makedirs('output', exist_ok=True)
    
    await parse_krasnoe_beloe_remote()


if __name__ == '__main__':
    asyncio.run(main())
