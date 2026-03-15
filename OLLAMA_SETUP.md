# Настройка Ollama для парсера

## Шаг 1: Установка Ollama

### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows
1. Скачайте установщик: https://ollama.com/download/OllamaSetup.exe
2. Запустите установщик
3. Ollama установится и запустится автоматически

### macOS
```bash
brew install ollama
```

## Шаг 2: Запуск Ollama

Ollama должна работать в фоне. Проверьте:
```bash
ollama --version
```

Если не запущена:
```bash
ollama serve
```

## Шаг 3: Загрузка модели

Рекомендуемые модели для парсинга:

### Qwen 2.5 (7B) - рекомендуется
```bash
ollama pull qwen2.5:7b
```

### Llama 3.2 (3B) - быстрее, меньше требований
```bash
ollama pull llama3.2:3b
```

### Mistral (7B) - хорошее качество
```bash
ollama pull mistral:7b
```

### Gemma 2 (9B) - от Google
```bash
ollama pull gemma2:9b
```

## Шаг 4: Настройка проекта

1. Откройте `.env` в проекте:
```
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:7b
USE_LLM=true
```

2. Измените модель если нужно:
```
OLLAMA_MODEL=llama3.2:3b
```

## Шаг 5: Запуск парсера

```bash
pip install -r requirements.txt
python main.py
```

## Проверка работы

Проверьте что Ollama отвечает:
```bash
curl http://localhost:11434/api/tags
```

Должны увидеть список загруженных моделей.

## Требования к железу

| Модель | RAM | VRAM (GPU) | Скорость |
|--------|-----|------------|----------|
| qwen2.5:7b | 8 GB | 4 GB | ~5 ток/сек |
| llama3.2:3b | 4 GB | 2 GB | ~15 ток/сек |
| mistral:7b | 8 GB | 4 GB | ~5 ток/сек |
| gemma2:9b | 12 GB | 6 GB | ~3 ток/сек |

**Без GPU** тоже работает, но медленнее (через CPU).

## Изменение модели

В `.env`:
```
OLLAMA_MODEL=llama3.2:3b
```

Или в коде `config.py`:
```python
OLLAMA_MODEL = 'qwen2.5:7b'
```

## Troubleshooting

### Ollama не отвечает
```bash
# Перезапустить
ollama serve
```

### Модель не загружается
```bash
# Проверить интернет
ollama pull qwen2.5:7b --insecure
```

### Мало памяти
Используйте меньшую модель:
```bash
ollama pull llama3.2:1b
```

### Медленно работает
- Закройте лишние программы
- Используйте меньшую модель
- Добавьте GPU если есть
