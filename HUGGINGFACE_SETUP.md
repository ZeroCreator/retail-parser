# Инструкция по получению API ключа Hugging Face

## Шаг 1: Регистрация

1. Перейдите на https://huggingface.co/join
2. Нажмите **Sign Up** (Зарегистрироваться)
3. Заполните форму:
   - **Email** — ваша почта
   - **Username** — имя пользователя
   - **Password** — пароль
4. Нажмите **Sign Up**
5. Подтвердите email (письмо придёт на почту)

## Шаг 2: Создание токена

1. Войдите в аккаунт на https://huggingface.co
2. Кликните на аватар в правом верхнем углу
3. Выберите **Settings** (Настройки)
4. В меню слева выберите **Access Tokens**
5. Нажмите кнопку **New token** (Новый токен)
6. Заполните:
   - **Name**: `retail-parser` (любое название)
   - **Type**: `Read` (чтение)
7. Нажмите **Generate token**
8. **Скопируйте токен** (он начинается с `hf_`)

## Шаг 3: Настройка проекта

1. Откройте файл `.env` в проекте
2. Добавьте токен:
```
LLM_PROVIDER=huggingface
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Готово!

Теперь можно запускать парсер:
```bash
python main.py
```

---

## Лимиты бесплатного тарифа

- ~1000 запросов в день
- Модели: Qwen, Mistral, Llama и другие
- Скорость: средняя (может быть очередь)

## Альтернативы

Если Hugging Face не работает, попробуйте:

### Groq Cloud (быстрее)
1. https://console.groq.com/
2. Войти через Google/GitHub
3. Keys → Create API Key
4. Бесплатно: ~30 запросов/минуту

### Google AI Studio
1. https://aistudio.google.com/
2. Войти через Google
3. Get API Key
4. Бесплатно: ~60 запросов/минуту
