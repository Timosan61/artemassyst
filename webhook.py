"""
🤖 artemmyassyst Bot Webhook Server

Telegram бот для работы с недвижимостью в Сочи.
AI-агент "Алёна" с интеллектуальной системой памяти.

Возможности:
- Обработка сообщений пользователей
- AI-powered ответы через OpenAI/Anthropic
- Интеллектуальная система памяти через ZEP
- Автоматическая установка webhook
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
import telebot
import json

# Добавляем путь для импорта модулей бота
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🚀 Загрузка artemmyassyst Bot Webhook Server...")

# Импорт structured logging
try:
    from utils.structured_logger import (
        log_webhook_received, log_ai_response, log_voice_message,
        log_error, log_business_connection
    )
    STRUCTURED_LOGGING = True
    print("✅ Structured logging загружен")
except ImportError:
    STRUCTURED_LOGGING = False
    print("⚠️ Structured logging недоступен")

# Импорт AI agent
try:
    from bot.agent import AlenaAgent
    agent = AlenaAgent()
    AI_ENABLED = True
    print("✅ AI Agent загружен успешно")
except ImportError as e:
    agent = None
    AI_ENABLED = False
    print(f"⚠️ AI Agent недоступен: {e}")

# === НАСТРОЙКИ ===
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBHOOK_SECRET_TOKEN = os.getenv("WEBHOOK_SECRET_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN отсутствует!")

print(f"✅ Токен бота: {TELEGRAM_BOT_TOKEN[:20]}...")

# === СОЗДАНИЕ БОТА ===
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Хранилище активных сессий пользователей для сохранения контекста
user_sessions = {}  # {user_id: session_id}

# === ЛОГИРОВАНИЕ ===
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Файловый handler
file_handler = logging.FileHandler("logs/bot.log", encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Консольный handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# === FASTAPI ПРИЛОЖЕНИЕ ===
app = FastAPI(
    title="artemmyassyst Bot Webhook",
    description="Telegram бот для работы с недвижимостью в Сочи",
    version="2.0"
)

# === СЧЕТЧИКИ ===
update_counter = 0
last_updates = []

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

async def send_human_like_response(chat_id: int, text: str, user_name: str = None):
    """Отправляет ответ с имитацией человеческого поведения"""
    try:
        # Имитация набора текста
        typing_delay = min(len(text) * 0.02, 3.0)  # Максимум 3 секунды

        bot.send_chat_action(chat_id, 'typing')
        await asyncio.sleep(typing_delay)

        # Отправляем сообщение
        bot.send_message(chat_id, text, parse_mode='Markdown')

        logger.info(f"✅ Ответ отправлен пользователю {user_name or chat_id}")

    except Exception as e:
        logger.error(f"❌ Ошибка отправки ответа: {e}")
        # Пробуем без Markdown
        try:
            bot.send_message(chat_id, text)
        except Exception as e2:
            logger.error(f"❌ Критическая ошибка отправки: {e2}")

def extract_user_info(message_data):
    """Извлекает информацию о пользователе из сообщения"""
    try:
        user = message_data.get('from', {})
        user_id = user.get('id')
        first_name = user.get('first_name', 'Аноним')
        last_name = user.get('last_name', '')
        username = user.get('username', '')

        # Формируем полное имя
        user_name = first_name
        if last_name:
            user_name += f" {last_name}"

        return user_id, user_name, username
    except Exception as e:
        logger.error(f"❌ Ошибка извлечения информации о пользователе: {e}")
        return None, "Аноним", ""

# === WEBHOOK ENDPOINTS ===

@app.get("/")
async def root():
    """Главная страница с информацией о боте"""
    return {
        "service": "artemmyassyst Bot Webhook",
        "status": "✅ Активен",
        "bot_name": "@artemmyassyst_bot",
        "ai_enabled": AI_ENABLED,
        "updates_processed": update_counter,
        "uptime": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Проверка состояния сервиса"""
    try:
        health_status = {
            "status": "healthy",
            "ai_enabled": AI_ENABLED,
            "bot_token_configured": bool(TELEGRAM_BOT_TOKEN),
            "webhook_secret_configured": bool(WEBHOOK_SECRET_TOKEN),
            "updates_processed": update_counter,
            "timestamp": datetime.now().isoformat()
        }

        # Проверяем AI agent
        if AI_ENABLED and agent:
            try:
                # Простая проверка что агент работает
                health_status["ai_status"] = "operational"
                health_status["zep_enabled"] = bool(agent.zep_client)
                health_status["memory_enabled"] = bool(agent.memory_service.enable_memory)
            except Exception as e:
                health_status["ai_status"] = f"error: {str(e)}"
                health_status["ai_enabled"] = False

        return health_status

    except Exception as e:
        logger.error(f"❌ Ошибка health check: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/webhook")
async def webhook(request: Request):
    """Основной webhook для обработки сообщений"""
    global update_counter, last_updates

    try:
        # Проверяем secret token
        if WEBHOOK_SECRET_TOKEN:
            token_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
            if token_header != WEBHOOK_SECRET_TOKEN:
                logger.warning(f"❌ Неверный secret token: {token_header}")
                raise HTTPException(status_code=403, detail="Forbidden")

        # Получаем данные
        data = await request.json()
        update_counter += 1

        # Сохраняем последние обновления
        last_updates.append({
            "timestamp": datetime.now().isoformat(),
            "update_id": data.get('update_id'),
            "type": "message" if 'message' in data else "business_message" if 'business_message' in data else "unknown"
        })
        if len(last_updates) > 10:
            last_updates.pop(0)

        # Structured logging
        if STRUCTURED_LOGGING:
            try:
                log_webhook_received(
                    update_id=data.get('update_id', 0),
                    message_type="message" if 'message' in data else "business_message",
                    has_ai=AI_ENABLED
                )
            except Exception:
                pass

        # Обрабатываем обычное сообщение
        if 'message' in data:
            await process_regular_message(data['message'])

        # Обрабатываем Business API сообщение
        elif 'business_message' in data:
            await process_business_message(data['business_message'])

        else:
            logger.info(f"ℹ️ Неизвестный тип update: {list(data.keys())}")

        return {"ok": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Критическая ошибка webhook: {e}")
        if STRUCTURED_LOGGING:
            try:
                log_error(
                    error_type="webhook_critical_error",
                    error_message=str(e),
                    user_id="unknown",
                    user_name="unknown"
                )
            except Exception:
                pass
        return {"ok": False, "error": str(e)}

async def process_regular_message(message_data):
    """Обработка обычного сообщения"""
    try:
        chat_id = message_data.get('chat', {}).get('id')
        message_id = message_data.get('message_id')
        text = message_data.get('text', '')
        message_type = "text"

        # Определяем тип сообщения
        if 'voice' in message_data:
            message_type = "voice"
        elif 'document' in message_data:
            message_type = "document"
        elif 'photo' in message_data:
            message_type = "photo"

        # Извлекаем информацию о пользователе
        user_id, user_name, username = extract_user_info(message_data)

        logger.info(f"📨 Сообщение от {user_name} (ID: {user_id}): {text[:100] if text else message_type}")

        # Генерируем ответ через AI
        if AI_ENABLED and agent and text:
            try:
                # Получаем или создаем session_id для пользователя
                user_key = str(user_id)
                session_id = user_sessions.get(user_key, user_key)

                response, real_session_id = await agent.generate_response(
                    text,
                    session_id,
                    user_name,
                    chat_id=str(chat_id),
                    existing_session_id=session_id if user_key in user_sessions else None
                )

                # Сохраняем НАСТОЯЩИЙ session_id для следующих сообщений
                user_sessions[user_key] = real_session_id

                # Structured logging
                if STRUCTURED_LOGGING:
                    try:
                        log_ai_response(
                            user_id=str(user_id),
                            user_name=user_name,
                            input_text=text,
                            response_text=response,
                            ai_enabled=True,
                            response_time=1.0,  # Приблизительное время
                            session_id=session_id
                        )
                    except Exception:
                        pass

            except Exception as ai_error:
                logger.error(f"❌ Ошибка AI генерации: {ai_error}")

                if STRUCTURED_LOGGING:
                    try:
                        log_error(
                            error_type="ai_generation_error",
                            error_message=str(ai_error),
                            user_id=str(user_id),
                            user_name=user_name,
                            input_text=text
                        )
                    except Exception:
                        pass

                response = f"Здравствуйте, {user_name}! Я Алёна, ваш персональный менеджер по недвижимости в Сочи. Чем могу помочь?"

        elif text:
            # Fallback если AI недоступен
            response = f"👋 {user_name}, получил ваш вопрос! Подготовлю ответ. Минуточку!\n\n⚠️ Внимание: AI временно недоступен, работаю в упрощенном режиме."

        elif message_type == "voice":
            response = f"🎤 {user_name}, получил ваше голосовое сообщение!\n\n⚠️ К сожалению, обработка голосовых сообщений временно недоступна.\n\nПожалуйста, напишите ваш вопрос текстом."

            if STRUCTURED_LOGGING:
                try:
                    log_voice_message(
                        user_id=str(user_id),
                        user_name=user_name,
                        processed=False,
                        error="Voice processing not available"
                    )
                except Exception:
                    pass
        else:
            logger.info(f"ℹ️ Неподдерживаемый тип сообщения '{message_type}' от {user_name}")
            return {"ok": True, "action": "no_action"}

        # Отправляем ответ
        await send_human_like_response(chat_id, response, user_name=user_name)

    except Exception as e:
        logger.error(f"❌ Ошибка обработки сообщения: {e}")

async def process_business_message(business_data):
    """Обработка Business API сообщения"""
    try:
        chat_id = business_data.get('chat', {}).get('id')
        text = business_data.get('text', '')

        user_id, user_name, username = extract_user_info(business_data)

        logger.info(f"💼 Business сообщение от {user_name}: {text[:100]}")

        if STRUCTURED_LOGGING:
            try:
                log_business_connection(
                    user_id=str(user_id),
                    user_name=user_name,
                    message_preview=text[:100],
                    connection_type="business_api"
                )
            except Exception:
                pass

        # Обрабатываем как обычное сообщение
        await process_regular_message(business_data)

    except Exception as e:
        logger.error(f"❌ Ошибка обработки Business сообщения: {e}")

@app.post("/set-webhook")
async def set_webhook():
    """Устанавливает webhook для бота"""
    try:
        webhook_url = "https://artemassyst-bot-tt5dt.ondigitalocean.app/webhook"

        # Настройки webhook
        webhook_data = {
            "url": webhook_url,
            "secret_token": WEBHOOK_SECRET_TOKEN,
            "allowed_updates": ["message", "business_message"]
        }

        # Устанавливаем webhook
        response = bot.set_webhook(**webhook_data)

        if response:
            logger.info(f"✅ Webhook установлен: {webhook_url}")
            return {
                "status": "✅ SUCCESS",
                "webhook_url": webhook_url,
                "secret_token_set": bool(WEBHOOK_SECRET_TOKEN),
                "allowed_updates": "✅ Business API включен"
            }
        else:
            return {"status": "❌ FAILED"}

    except Exception as e:
        logger.error(f"❌ Ошибка установки webhook: {e}")
        return {"status": "❌ ERROR", "error": str(e)}

# === ADMIN ENDPOINTS ===

@app.get("/admin/dialogs/stats")
async def get_dialog_stats():
    """Получить статистику по диалогам"""
    try:
        from bot.dialog_logger import dialog_logger
        stats = dialog_logger.get_dialog_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/admin/dialogs/user/{user_id}")
async def get_user_dialog(user_id: str, limit: int = 20):
    """Получить диалог конкретного пользователя"""
    try:
        from bot.dialog_logger import dialog_logger
        messages = dialog_logger.get_user_dialog(user_id, limit)
        return {
            "status": "success",
            "user_id": user_id,
            "messages_count": len(messages),
            "data": messages
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/admin/dialogs/recent")
async def get_recent_dialogs(limit: int = 50):
    """Получить последние диалоги всех пользователей"""
    try:
        from bot.dialog_logger import dialog_logger
        messages = dialog_logger.get_all_recent_dialogs(limit)
        return {
            "status": "success",
            "messages_count": len(messages),
            "data": messages
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/admin/dialogs/search")
async def search_dialogs(query: str, user_id: str = None, limit: int = 50):
    """Поиск по диалогам"""
    try:
        from bot.dialog_logger import dialog_logger
        results = dialog_logger.search_dialogs(query, user_id)
        return {
            "status": "success",
            "query": query,
            "user_id": user_id,
            "results_count": len(results),
            "data": results[:limit]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/admin/dialogs/export/{user_id}")
async def export_user_dialog(user_id: str, format: str = "json"):
    """Экспорт диалога пользователя"""
    try:
        from bot.dialog_logger import dialog_logger
        from fastapi.responses import PlainTextResponse

        exported_data = dialog_logger.export_user_dialog(user_id, format)
        if not exported_data:
            return {"error": "Диалог пользователя не найден"}

        if format == "txt":
            return PlainTextResponse(exported_data,
                                   media_type="text/plain; charset=utf-8")
        else:
            return PlainTextResponse(exported_data,
                                   media_type="application/json; charset=utf-8")
    except Exception as e:
        return {"error": str(e)}

@app.post("/admin/reload-prompt")
async def reload_prompt():
    """Перезагрузить инструкции бота"""
    try:
        if AI_ENABLED and agent is not None:
            old_updated = agent.instruction.get('last_updated', 'неизвестно')
            agent.reload_instruction()
            new_updated = agent.instruction.get('last_updated', 'неизвестно')

            return {
                "status": "success",
                "changed": old_updated != new_updated,
                "old_updated": old_updated,
                "new_updated": new_updated,
                "instruction_length": len(agent.instruction.get("system_instruction", ""))
            }
        else:
            return {"error": "AI agent не загружен"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/admin/sheets/sync")
async def sync_google_sheets():
    """Ручная синхронизация данных с Google Sheets"""
    try:
        if AI_ENABLED and agent is not None:
            sync_success = await agent.manual_sheets_sync()
            sheets_url = await agent.get_sheets_url()

            return {
                "status": "success" if sync_success else "partial",
                "sync_completed": sync_success,
                "sheets_url": sheets_url,
                "sheets_enabled": hasattr(agent, 'sheets_service') and agent.sheets_service is not None
            }
        else:
            return {"error": "AI agent не загружен"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn

    # Логирование запуска
    logger.info("🚀 artemmyassyst Webhook server started")
    logger.info(f"📁 Logs directory: {os.path.abspath('logs')}")
    logger.info(f"🤖 Bot token: {TELEGRAM_BOT_TOKEN[:20]}...")
    logger.info(f"🔄 AI Agent enabled: {AI_ENABLED}")

    if WEBHOOK_SECRET_TOKEN:
        logger.info(f"🔐 Webhook secret configured")
    else:
        logger.warning("⚠️ Webhook secret not configured")

    # Запуск сервера
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)