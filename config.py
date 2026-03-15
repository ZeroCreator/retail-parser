import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '1.0'))
    TIMEOUT = int(os.getenv('TIMEOUT', '30'))
    RETRY_COUNT = int(os.getenv('RETRY_COUNT', '3'))
    OUTPUT_FORMAT = os.getenv('OUTPUT_FORMAT', 'csv')
    
    # LLM settings
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'ollama')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5:7b')
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    USE_LLM = os.getenv('USE_LLM', 'true').lower() == 'true'
    
    OUTPUT_DIR = 'output'
    
    # Store URLs
    STORES = {
        'x5': 'https://5ka.ru',
        'magnit': 'https://magnit.ru',
        'yarche': 'https://yarche.ru', # организация съемок - непонятно что парсить
        'kb': 'https://krasnoeibeloe.ru', # есть каталог
        'maria_ra': 'https://maria-ra.ru',
        'chizhik': 'https://chizhik.club/'
    }
