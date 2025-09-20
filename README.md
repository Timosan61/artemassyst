# artemmyassyst Bot

🤖 Telegram бот для работы с недвижимостью в Сочи с AI-агентом "Алёна"

## Описание

AI-ассистент для консультации по недвижимости в Сочи с интеллектуальной системой памяти.

## Возможности

- 🤖 **AI-агент "Алёна"** - персональный менеджер по недвижимости
- 🧠 **OpenAI/Anthropic** - умные ответы через ведущие LLM
- 💾 **ZEP Cloud** - интеллектуальная система памяти
- 🚀 **Railway** - автоматический деплой
- 📊 **Google Sheets** - интеграция для CRM
- 🔗 **Webhook** - мгновенные ответы

## Быстрый старт

### 1. Настройка переменных окружения

Создайте файл `.env`:

```env
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
BOT_USERNAME=@artem_integrator_bot
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
ZEP_API_KEY=YOUR_ZEP_API_KEY_HERE
WEBHOOK_SECRET_TOKEN=YOUR_WEBHOOK_SECRET_HERE
ADMIN_PASSWORD=YOUR_ADMIN_PASSWORD_HERE
```

### 2. Локальный запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск webhook сервера
python webhook.py
```

### 3. Деплой на Railway

1. Подключите GitHub репозиторий к Railway
2. Установите переменные окружения в Railway Dashboard
3. Railway автоматически задеплоит проект

## Управление ботом

### Основные эндпоинты

- `/` - Health check и статус бота
- `/webhook` - Webhook для Telegram
- `/set-webhook` - Установка webhook
- `/admin/reload-prompt` - Перезагрузка инструкций
- `/admin/sheets/sync` - Синхронизация Google Sheets

## Конфигурация

### Инструкции для LLM

Инструкции хранятся в `data/instruction.json`:

```json
{
  "system_instruction": "Ваша системная инструкция...",
  "welcome_message": "Приветственное сообщение",
  "last_updated": "2025-01-27T12:00:00"
}
```

### Основные настройки

- `bot/config.py` - Конфигурация бота
- `requirements.txt` - Python зависимости  
- `Dockerfile.complete` - Docker контейнер
- `railway.json` - Настройки Railway деплоя

## Особенности

### Интеллектуальная система памяти

- **ZEP Cloud** - продвинутая система запоминания диалогов
- **Квалификация лидов** - автоматическая оценка потенциала клиентов
- **Система состояний** - отслеживание этапа диалога
- **Google Sheets** - синхронизация данных для CRM

### Мониторинг и отладка

- Ротируемые логи в `logs/bot.log`
- Health check для проверки статуса
- Structured logging для аналитики

## Архитектура

- **webhook.py** - FastAPI веб-сервер для Telegram webhook
- **bot/agent.py** - AI-агент с системой памяти
- **bot/memory/** - модули интеллектуальной памяти
- **bot/integrations/** - интеграции с внешними сервисами

## Версия

Версия: 2.0 (после рефакторинга)

---

*Создано автоматически системой клонирования ботов* 🤖