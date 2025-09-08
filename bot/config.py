import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
ZEP_API_KEY = os.getenv('ZEP_API_KEY', '')
BOT_USERNAME = os.getenv('BOT_USERNAME')

# Google Sheets Integration
GOOGLE_SHEETS_ENABLED = os.getenv('GOOGLE_SHEETS_ENABLED', 'false').lower() == 'true'
GOOGLE_SHEETS_SYNC_INTERVAL = int(os.getenv('GOOGLE_SHEETS_SYNC_INTERVAL', '3600'))  # 1 час по умолчанию

# Абсолютный путь к файлу инструкций
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTRUCTION_FILE = os.path.join(BASE_DIR, 'data', 'instruction.json')
OPENAI_MODEL = 'gpt-4o'
ANTHROPIC_MODEL = 'claude-3-5-sonnet-20241022'

# === LLM ПАРАМЕТРЫ ДЛЯ ЖИВОГО ОБЩЕНИЯ ===
# Параметры OpenAI для имитации естественного диалога
OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.8'))  # Было 0.7, увеличиваем для спонтанности
OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '1000'))
OPENAI_PRESENCE_PENALTY = float(os.getenv('OPENAI_PRESENCE_PENALTY', '0.6'))  # Поощряет новые темы
OPENAI_FREQUENCY_PENALTY = float(os.getenv('OPENAI_FREQUENCY_PENALTY', '0.2'))  # Снижает повторы
OPENAI_TOP_P = float(os.getenv('OPENAI_TOP_P', '0.9'))  # Контроль креативности

# Параметры Anthropic для совместимости
ANTHROPIC_TEMPERATURE = float(os.getenv('ANTHROPIC_TEMPERATURE', '0.8'))
ANTHROPIC_MAX_TOKENS = int(os.getenv('ANTHROPIC_MAX_TOKENS', '1000'))

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")
# === AI AGENT SETTINGS ===
AI_ENABLED = bool(OPENAI_API_KEY or ANTHROPIC_API_KEY)  # AI включен если есть хоть один ключ

# Проверки API ключей (не критичные для запуска)
if not OPENAI_API_KEY:
    print("⚠️ OPENAI_API_KEY не найден в переменных окружения")
if not ZEP_API_KEY:
    print("⚠️ ZEP_API_KEY не найден в переменных окружения")