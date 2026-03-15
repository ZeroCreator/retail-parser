# Retail Parser с Ollama

Парсер товаров для российских розничных сетей с использованием **локальной LLM через Ollama**.

## Магазины

- X5 (Пятёрочка) - https://5ka.ru/catalog/ видны каталоги, однако товары в них не отображаются.
- Магнит - https://magnit.ru/catalog - товары есть
- Ярче - https://yarche.ru/ - непонятно что собирать (студия рекламных роликов)
- Красное & Белое - https://krasnoeibeloe.ru/catalog/ - видны подкаталоги, есть товары
- Мария Ра - https://www.maria-ra.ru/aktsii/ - подгружается по кнопке
- Чижик - https://chizhik.club/catalog/?cityId=c1cfe4b9-f7c2-423c-abfa-6ed1c05a15c5 - не загружается каталог

## 🚀 Быстрый старт

### 1. Установить Ollama

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Загрузить модель

```bash
ollama pull qwen2.5:7b
```

### 3. Настроить проект

```bash
cd retail-parser
pip install -r requirements.txt
```

### 4. Запустить парсер

```bash
python main.py
```

## ⚙️ Конфигурация

Файл `.env`:

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:7b
USE_LLM=true
```

## 📊 Выходные данные

Файлы в папке `output/`:
- `{store}_{timestamp}.csv` — товары по магазину
- `all_stores_{timestamp}.csv` — все товары
- `parser.log` — лог работы


```dotenv
# Environment configuration
REQUEST_DELAY=1.0
TIMEOUT=30
RETRY_COUNT=3
OUTPUT_FORMAT=csv
# OUTPUT_FORMAT=excel

# LLM Provider (ollama, huggingface, groq, google, openai, anthropic, dashscope)
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:7b

# Ollama (локально, бесплатно) - http://localhost:11434
# Не требует API ключа

# Hugging Face (бесплатно) - https://huggingface.co/join
HUGGINGFACE_API_KEY=your_key_here

# Groq Cloud (бесплатно) - https://console.groq.com/
GROQ_API_KEY=your_key_here

# Google AI Studio (бесплатно) - https://aistudio.google.com/
GOOGLE_API_KEY=your_key_here

# OpenAI
OPENAI_API_KEY=your_key_here

# Anthropic
ANTHROPIC_API_KEY=your_key_here

# DashScope
DASHSCOPE_API_KEY=your_key_here

# Use LLM parsing
USE_LLM=true

```