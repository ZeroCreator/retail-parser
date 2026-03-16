# Remote Debugging Парсер

Этот подход позволяет использовать **существующий браузер Chrome** с открытым remote-debugging-port вместо запуска нового headless браузера.

## Преимущества

✅ **Обход анти-бот защиты** - браузер выглядит как обычный пользовательский  
✅ **Отладка в реальном времени** - можно видеть, что происходит в браузере  
✅ **Сохранение сессии** - cookies, localStorage, авторизации сохраняются  
✅ **Ручное вмешательство** - можно вручную пройти капчу или кликнуть кнопки  

## Инструкция

### 1. Запуск Chrome с Remote Debugging

```bash
google-chrome-stable --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug google.com
```

**Параметры:**
- `--remote-debugging-port=9222` - порт для отладки
- `--user-data-dir=/tmp/chrome-debug` - отдельный профиль (чтобы не конфликтовал с основным)
- `google.com` - любая стартовая страница

**Для macOS:**
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug
```

**Для Windows:**
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug
```

### 2. Запуск парсера

```bash
cd ai-test
python parse_kb_remote.py
```

### 3. Использование в основном проекте

В файле `.env`:
```env
USE_REMOTE_DEBUG=true
REMOTE_DEBUG_PORT=9222
```

Затем запустите основной парсер:
```bash
python main_kb.py
```

## Как это работает

1. **Playwright** подключается к существующему браузеру через **Chrome DevTools Protocol (CDP)**
2. Браузер уже запущен с вашим профилем, cookies и настройками
3. Парсер создает новую вкладку в существующем браузере
4. После завершения парсера браузер остается работать (не закрывается)

## Пример кода

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    # Подключение к существующему браузеру
    browser = await p.chromium.connect_over_cdp('http://localhost:9222')
    
    # Использование существующего контекста или создание нового
    if browser.contexts:
        context = browser.contexts[0]
    else:
        context = await browser.new_context()
    
    # Создание новой страницы
    page = await context.new_page()
    await page.goto('https://krasnoeibeloe.ru/catalog/')
    
    # Парсинг...
```

## Отладка

### Проверка подключения

Откройте в другом браузере: `http://localhost:9222/json`

Вы увидите список активных вкладок в формате JSON.

### Chrome DevTools

Можно подключиться к отладке через Chrome:
1. Откройте `chrome://inspect`
2. Найдите "Remote Target"
3. Кликните "inspect" на нужной вкладке

## Решение проблем

### Ошибка: "Connection refused"
- Убедитесь, что Chrome запущен с правильными параметрами
- Проверьте, что порт 9222 не занят: `lsof -i :9222`
- Попробуйте другой порт: `--remote-debugging-port=9223`

### Ошибка: "Browser closed unexpectedly"
- Закройте все другие экземпляры Chrome
- Удалите папку профиля: `rm -rf /tmp/chrome-debug`
- Запустите Chrome заново

### Парсер не видит товары
- Откройте DevTools (`http://localhost:9222/json`)
- Проверьте, что страница полностью загрузилась
- Увеличьте время ожидания: `await page.wait_for_timeout(10000)`

## Сравнение подходов

| Подход | Headless | Обход защиты | Скорость | Отладка |
|--------|----------|--------------|----------|---------|
| **Обычный Playwright** | ✅ | ❌ | ⚡⚡⚡ | ❌ |
| **Remote Debugging** | ❌ | ✅ | ⚡⚡ | ✅ |
| **С видимым браузером** | ❌ | ⚡ | ⚡⚡ | ✅ |

## Дополнительные ресурсы

- [Playwright CDP Documentation](https://playwright.dev/python/docs/api/class-browsertype#browser-type-connect-over-cdp)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Remote Debugging](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/docs/linux/using_chrome.md#remote-debugging)
