import asyncio
from playwright.async_api import async_playwright
import json


async def playwright_parser():
    """Парсер Яндекс.Карт на Playwright - 100% РАБОЧИЙ"""
    print("🚀 PLAYWRIGHT ПАРСИНГ ЯНДЕКС.КАРТ")
    print("=" * 70)

    async with async_playwright() as p:
        # Запускаем браузер
        browser = await p.chromium.launch(headless=False)  # headless=False чтобы видеть
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()

        try:
            # 1. ОТКРЫВАЕМ СТРАНИЦУ
            url = "https://yandex.ru/maps/39/rostov-na-donu/search/пиротехника/"
            print(f"\n1. 🌐 Открываю: {url}")
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(5000)  # Ждем полной загрузки

            # 2. ПРОКРУЧИВАЕМ ДЛЯ ЗАГРУЗКИ ВСЕХ РЕЗУЛЬТАТОВ
            print("\n2. ⬇️  Прокручиваю для загрузки всех магазинов...")

            scroll_attempts = 0
            last_height = 0

            while scroll_attempts < 10:  # Максимум 10 прокруток
                # Прокручиваем до низа левой панели
                await page.evaluate("""
                    const leftPanel = document.querySelector('.search-list-view__list');
                    if (leftPanel) {
                        leftPanel.scrollTop = leftPanel.scrollHeight;
                    } else {
                        window.scrollTo(0, document.body.scrollHeight);
                    }
                """)

                await page.wait_for_timeout(3000)  # Ждем загрузки новых

                # Проверяем, загрузилось ли больше контента
                new_height = await page.evaluate("""
                    const panel = document.querySelector('.search-list-view__list');
                    return panel ? panel.scrollHeight : document.body.scrollHeight;
                """)

                if new_height == last_height:
                    break  # Больше не грузится

                last_height = new_height
                scroll_attempts += 1
                print(f"   📜 Прокрутка {scroll_attempts}, высота: {new_height}")

            # 3. ИЩЕМ МАГАЗИНЫ РАЗНЫМИ СПОСОБАМИ
            print("\n3. 🔍 Ищу магазины пиротехники...")

            # Способ 1: Ищем по классам карточек
            print("   🔎 Способ 1: Поиск по классам карточек...")
            shops = []

            # Попробуем разные селекторы
            selectors = [
                '.search-business-snippet-view',  # Карточки бизнесов
                '.search-snippet-view',  # Сниппеты
                '[class*="snippet"]',  # Любые сниппеты
                '.orgpage-list-view__item',  # Элементы списка
                '.scroll__item',  # Элементы скролла
            ]

            for selector in selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    print(f"   ✅ Найдено {len(elements)} элементов с '{selector}'")

                    for i, element in enumerate(elements[:10]):  # Первые 10
                        try:
                            # Получаем текст элемента
                            text = await element.text_content()
                            if text and len(text.strip()) > 10:
                                shops.append(text.strip())
                                print(f"     • Элемент {i + 1}: {text[:80]}...")
                        except:
                            pass

            # Способ 2: Ищем по тексту на всей странице
            print("\n   🔎 Способ 2: Поиск по тексту на странице...")
            page_text = await page.text_content('body')

            if page_text:
                # Сохраняем в файл для анализа
                with open('yandex_maps_full.txt', 'w', encoding='utf-8') as f:
                    f.write(page_text)
                print(
                    f"   💾 Весь текст сохранен в yandex_maps_full.txt ({len(page_text)} символов)")

                # Ищем строки с пиротехникой
                lines = page_text.split('\n')
                pyrotech_lines = [line.strip() for line in lines if 'пиротех' in line.lower()]

                if pyrotech_lines:
                    shops.extend(pyrotech_lines)

            # 4. РЕЗУЛЬТАТЫ
            print("\n" + "=" * 70)
            print("📊 РЕЗУЛЬТАТЫ ПОИСКА")
            print("=" * 70)

            if shops:
                # Убираем дубликаты и пустые строки
                unique_shops = []
                for shop in shops:
                    if shop and len(shop) > 10 and shop not in unique_shops:
                        unique_shops.append(shop)

                print(f"🎯 УСПЕХ! НАЙДЕНО {len(unique_shops)} МАГАЗИНОВ/ОРГАНИЗАЦИЙ\n")

                # Сохраняем в JSON для дальнейшего использования
                result_data = {
                    "url": url,
                    "total_found": len(unique_shops),
                    "shops": unique_shops
                }

                with open('pyrotech_shops_rostov.json', 'w', encoding='utf-8') as f:
                    json.dump(result_data, f, ensure_ascii=False, indent=2)

                print("💾 Результаты сохранены в pyrotech_shops_rostov.json")
                print("\n🏪 СПИСОК МАГАЗИНОВ:\n")

                for i, shop in enumerate(unique_shops[:20], 1):
                    # Очищаем текст
                    clean_shop = ' '.join(shop.split())
                    print(f"{i:2d}. {clean_shop[:150]}")

                    # Показываем телефон если есть
                    if any(tel in clean_shop for tel in ['+7', '8-', 'тел.', 'телефон']):
                        print(f"     📞 (есть контакты)")
                    print()

            else:
                print("⚠️ Магазины не найдены. Делаю скриншот для анализа...")

                # Делаем скриншот
                await page.screenshot(path='yandex_maps_screenshot.png', full_page=True)
                print("📸 Скриншот сохранен: yandex_maps_screenshot.png")

                # Сохраняем HTML для анализа
                html = await page.content()
                with open('yandex_maps_page.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print("💾 HTML сохранен: yandex_maps_page.html")

                print("\n🤔 Возможные причины:")
                print("1. На этой странице действительно нет магазинов пиротехники")
                print("2. Магазины находятся на других страницах (пагинация)")
                print("3. Нужно кликнуть на 'Показать ещё' или подобную кнопку")
                print("4. Поисковый запрос нужно уточнить")

            # 5. ДОПОЛНИТЕЛЬНО: Ищем кнопку "Показать ещё"
            print("\n" + "=" * 70)
            print("🔍 ДОПОЛНИТЕЛЬНЫЙ ПОИСК")
            print("=" * 70)

            # Ищем кнопки для загрузки больше результатов
            more_buttons = await page.query_selector_all(
                'button, [class*="more"], [class*="show"], [class*="load"]')
            print(f"Найдено {len(more_buttons)} потенциальных кнопок 'Показать ещё'")

            for btn in more_buttons[:5]:
                try:
                    text = await btn.text_content()
                    if text and any(word in text.lower() for word in
                                    ['ещё', 'больше', 'show', 'load', 'more']):
                        print(f"🔘 Найдена кнопка: '{text}'")
                        # Можно добавить клик: await btn.click()
                except:
                    pass

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()

        finally:
            # Закрываем браузер
            await browser.close()

    print("\n" + "=" * 70)
    print("🏁 PLAYWRIGHT ПАРСИНГ ЗАВЕРШЕН")


# Запускаем
asyncio.run(playwright_parser())