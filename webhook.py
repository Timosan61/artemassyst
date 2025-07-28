"""
🤖 artemmyassyst Bot Webhook Server

Автоматически сгенерированный webhook сервер для artemmyassyst.
Основан на Textile Pro Bot с адаптацией под новые требования.

Возможности:
- Обработка обычных сообщений боту
- Обработка Business API сообщений (от вашего Premium аккаунта)
- AI-powered ответы через OpenAI
- Память диалогов через Zep
- Автоматическая установка webhook при старте
"""

import os
import sys
import logging
import traceback
import time
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
import telebot
import json
import asyncio
import requests

# Добавляем путь для импорта модулей бота
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🚀 Загрузка artemmyassyst Bot Webhook Server...")

# Импорт structured logging
try:
    from utils.structured_logger import log_webhook_received, log_ai_response, log_voice_message, log_error, log_business_connection, log_api_key_issue, log_performance_metric
    print("✅ Structured logging загружен")
    STRUCTURED_LOGGING = True
except ImportError:
    print("⚠️ Structured logging недоступен")
    STRUCTURED_LOGGING = False

# Пытаемся импортировать AI agent
try:
    import bot
    print("✅ Модуль bot найден")
    from bot.agent import agent
    print("✅ AI Agent загружен успешно")
    AI_ENABLED = True
except ImportError as e:
    print(f"⚠️ AI Agent не доступен: {e}")
    print(f"📁 Текущая директория: {os.getcwd()}")
    print(f"📁 Файлы в директории: {os.listdir('.')}")
    if os.path.exists('bot'):
        print(f"📁 Файлы в bot/: {os.listdir('bot')}")
    AI_ENABLED = False
except Exception as e:
    print(f"❌ Ошибка загрузки AI Agent: {e}")
    AI_ENABLED = False

# === НАСТРОЙКИ ===
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBHOOK_SECRET_TOKEN = os.getenv("WEBHOOK_SECRET_TOKEN", "ikXktYv3Sd_h87wMYvcp1sHsQaSiIjxS_wQOCy7GGrY")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN отсутствует!")

print(f"✅ Токен бота получен: {TELEGRAM_BOT_TOKEN[:20]}...")

# === СОЗДАНИЕ СИНХРОННОГО БОТА (НЕ ASYNC!) ===
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# === ЛОГИРОВАНИЕ ===
import logging.handlers

# Создаем директорию для логов если её нет
os.makedirs("logs", exist_ok=True)

# Настраиваем логирование в файл и консоль
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Формат логов
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Файловый хендлер с ротацией
file_handler = logging.handlers.RotatingFileHandler(
    filename="logs/bot.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

# Консольный хендлер
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# Добавляем хендлеры к логгеру
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Логируем запуск приложения
logger.info("🚀 artemmyassyst Webhook server started")
logger.info(f"📁 Logs directory: {os.path.abspath('logs')}")
logger.info(f"🤖 Bot token: {TELEGRAM_BOT_TOKEN[:20]}...")
logger.info(f"🔄 AI Agent enabled: {AI_ENABLED}")

# === ФУНКЦИЯ ДЛЯ BUSINESS API ===
def send_business_message(chat_id, text, business_connection_id):
    """
    Отправка сообщения через Business API используя прямой HTTP запрос
    (pyTelegramBotAPI не поддерживает business_connection_id)
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "business_connection_id": business_connection_id
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            logger.info(f"✅ Business API: сообщение отправлено через HTTP API")
            return result.get("result")
        else:
            logger.error(f"❌ Business API ошибка: {result}")
            return None
    except Exception as e:
        logger.error(f"❌ Business API HTTP ошибка: {e}")
        return None

# === FASTAPI ПРИЛОЖЕНИЕ ===
app = FastAPI(
    title="🤖 artemmyassyst Bot", 
    description="Webhook-only режим для artemmyassyst бота"
)

# Хранилище последних updates для отладки
from collections import deque
last_updates = deque(maxlen=10)
update_counter = 0

# Хранилище владельцев Business Connection для фильтрации сообщений
business_owners = {}  # {business_connection_id: owner_user_id}

@app.get("/")
async def health_check():
    """Health check endpoint"""
    try:
        bot_info = bot.get_me()
        
        # Детальная информация об AI статусе
        ai_details = {
            "ai_enabled_in_code": AI_ENABLED,
            "openai_key_configured": bool(os.getenv('OPENAI_API_KEY')),
            "openai_key_length": len(os.getenv('OPENAI_API_KEY', '')),
            "agent_loaded": 'agent' in globals(),
            "openai_client_status": "configured" if (AI_ENABLED and agent and agent.openai_client) else "missing"
        }
        
        return {
            "status": "🟢 ONLINE", 
            "service": "artemmyassyst Bot Webhook",
            "bot": f"@{bot_info.username}",
            "bot_id": bot_info.id,
            "mode": "WEBHOOK_ONLY",
            "ai_status": "✅ ENABLED" if AI_ENABLED else "❌ DISABLED",
            "openai_configured": bool(os.getenv('OPENAI_API_KEY')),
            "ai_details": ai_details,
            "debug_info": {
                "total_updates_processed": update_counter,
                "business_connections": len(business_owners),
                "last_update_time": last_updates[-1]['timestamp'] if last_updates else None
            },
            "endpoints": {
                "webhook_info": "/webhook/info",
                "set_webhook": "/webhook/set",
                "delete_webhook": "/webhook (DELETE method)",
                "debug_logs": "/debug/logs",
                "debug_config": "/debug/config", 
                "debug_ai_status": "/debug/ai-status",
                "debug_prompt": "/debug/prompt",
                "admin_reload": "/admin/reload-prompt",
                "business_owners": "/debug/business-owners",
                "last_updates": "/debug/last-updates",
                "structured_logs": "/debug/structured-logs",
                "recent_errors": "/debug/errors",
                "voice_stats": "/debug/voice-messages"
            },
            "hint": "Используйте /webhook/set в браузере для установки webhook"
        }
    except Exception as e:
        return {"status": "🔴 ERROR", "error": str(e)}

@app.get("/webhook/set")
async def set_webhook_get():
    """Установка webhook через GET (для браузера)"""
    return await set_webhook()

@app.post("/webhook/set")
async def set_webhook():
    """Установка webhook"""
    try:
        webhook_url = os.getenv("WEBHOOK_URL", "https://artemassyst-bot-tt5dt.ondigitalocean.app/webhook")
        
        result = bot.set_webhook(
            url=webhook_url,
            secret_token=WEBHOOK_SECRET_TOKEN,
            allowed_updates=[
                "message",
                "business_connection", 
                "business_message",
                "edited_business_message",
                "deleted_business_messages"
            ]
        )
        
        if result:
            logger.info(f"✅ Webhook установлен: {webhook_url}")
            return {
                "status": "✅ SUCCESS",
                "webhook_url": webhook_url,
                "secret_token": "✅ Настроен",
                "allowed_updates": "✅ Business API включен"
            }
        else:
            return {"status": "❌ FAILED"}
            
    except Exception as e:
        logger.error(f"❌ Ошибка установки webhook: {e}")
        return {"status": "❌ ERROR", "error": str(e)}

# === DEBUG ENDPOINTS ===
@app.get("/debug/logs")
async def get_debug_logs():
    """Получить последние логи для диагностики"""
    try:
        log_file = "logs/bot.log"
        if not os.path.exists(log_file):
            return {"error": "Log file not found", "file_path": log_file}
        
        # Читаем последние 100 строк
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            last_lines = lines[-100:] if len(lines) > 100 else lines
        
        return {
            "status": "success",
            "log_file": log_file,
            "total_lines": len(lines),
            "returned_lines": len(last_lines),
            "logs": [line.strip() for line in last_lines]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/config")
async def get_debug_config():
    """Получить конфигурацию бота (без секретных данных)"""
    try:
        config_info = {
            "ai_enabled": AI_ENABLED,
            "environment_variables": {
                "TELEGRAM_BOT_TOKEN": "***" + os.getenv('TELEGRAM_BOT_TOKEN', '')[-4:] if os.getenv('TELEGRAM_BOT_TOKEN') else "NOT_SET",
                "OPENAI_API_KEY": "***" + os.getenv('OPENAI_API_KEY', '')[-4:] if os.getenv('OPENAI_API_KEY') else "NOT_SET",
                "ANTHROPIC_API_KEY": "***" + os.getenv('ANTHROPIC_API_KEY', '')[-4:] if os.getenv('ANTHROPIC_API_KEY') else "NOT_SET",
                "ZEP_API_KEY": "***" + os.getenv('ZEP_API_KEY', '')[-4:] if os.getenv('ZEP_API_KEY') else "NOT_SET",
                "WEBHOOK_SECRET_TOKEN": "CONFIGURED" if WEBHOOK_SECRET_TOKEN else "NOT_SET"
            },
            "key_lengths": {
                "telegram_token": len(os.getenv('TELEGRAM_BOT_TOKEN', '')),
                "openai_key": len(os.getenv('OPENAI_API_KEY', '')),
                "anthropic_key": len(os.getenv('ANTHROPIC_API_KEY', '')),
                "zep_key": len(os.getenv('ZEP_API_KEY', ''))
            },
            "agent_status": {
                "agent_loaded": 'agent' in globals(),
                "openai_client": "configured" if (AI_ENABLED and 'agent' in globals() and agent.openai_client) else "missing",
                "zep_client": "configured" if (AI_ENABLED and 'agent' in globals() and agent.zep_client) else "missing"
            }
        }
        
        return {"status": "success", "config": config_info}
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/ai-status")
async def get_ai_status():
    """Детальный статус AI компонентов"""
    try:
        ai_status = {
            "ai_enabled_flag": AI_ENABLED,
            "agent_imported": 'agent' in globals()
        }
        
        if AI_ENABLED and 'agent' in globals():
            ai_status.update({
                "openai_client_exists": agent.openai_client is not None,
                "zep_client_exists": agent.zep_client is not None,
                "instruction_loaded": bool(agent.instruction),
                "user_sessions_count": len(agent.user_sessions) if hasattr(agent, 'user_sessions') else 0
            })
            
            # Проверка API ключей
            openai_key = os.getenv('OPENAI_API_KEY', '')
            if openai_key:
                ai_status["openai_key_format_valid"] = openai_key.startswith('sk-') and len(openai_key) > 40
                ai_status["openai_key_length"] = len(openai_key)
            else:
                ai_status["openai_key_missing"] = True
                
        return {"status": "success", "ai_status": ai_status}
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/business-owners")
async def get_business_owners():
    """Получить информацию о Business Connection владельцах"""
    try:
        return {
            "status": "success",
            "business_owners_count": len(business_owners),
            "business_owners": {conn_id: f"user_{user_id}" for conn_id, user_id in business_owners.items()}
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/last-updates")
async def get_last_updates():
    """Получить последние webhook updates для анализа"""
    try:
        return {
            "status": "success",
            "total_updates_processed": update_counter,
            "last_updates_count": len(last_updates),
            "last_updates": list(last_updates)
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/structured-logs")
async def get_structured_logs():
    """Получить structured logs в JSON формате"""
    try:
        log_file = "logs/structured.log"
        if not os.path.exists(log_file):
            return {"error": "Structured log file not found", "file_path": log_file}
        
        # Читаем последние 50 структурированных записей
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            last_lines = lines[-50:] if len(lines) > 50 else lines
        
        # Парсим JSON записи
        structured_logs = []
        for line in last_lines:
            try:
                log_entry = json.loads(line.strip())
                structured_logs.append(log_entry)
            except json.JSONDecodeError:
                # Пропускаем некорректные JSON строки
                pass
        
        return {
            "status": "success",
            "log_file": log_file,
            "total_lines": len(lines),
            "parsed_entries": len(structured_logs),
            "logs": structured_logs
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/errors")
async def get_recent_errors():
    """Получить последние ошибки из structured logs"""
    try:
        log_file = "logs/structured.log"
        if not os.path.exists(log_file):
            return {"error": "Structured log file not found"}
        
        errors = []
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            # Ищем ошибки в последних 100 строках
            for line in lines[-100:]:
                try:
                    log_entry = json.loads(line.strip())
                    if log_entry.get('level') in ['ERROR', 'CRITICAL'] or log_entry.get('event_type') == 'error':
                        errors.append(log_entry)
                except json.JSONDecodeError:
                    pass
        
        # Сортируем по времени (новые сверху)
        errors.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return {
            "status": "success",
            "error_count": len(errors),
            "errors": errors[:20]  # Последние 20 ошибок
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/voice-messages")
async def get_voice_messages_stats():
    """Статистика по голосовым сообщениям"""
    try:
        log_file = "logs/structured.log"
        if not os.path.exists(log_file):
            return {"error": "Structured log file not found"}
        
        voice_messages = []
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            for line in lines:
                try:
                    log_entry = json.loads(line.strip())
                    if log_entry.get('event_type') == 'voice_message':
                        voice_messages.append(log_entry)
                except json.JSONDecodeError:
                    pass
        
        # Статистика
        total_voice = len(voice_messages)
        processed_count = sum(1 for vm in voice_messages if vm.get('metadata', {}).get('processed', False))
        
        return {
            "status": "success",
            "total_voice_messages": total_voice,
            "processed_count": processed_count,
            "unprocessed_count": total_voice - processed_count,
            "recent_voice_messages": voice_messages[-10:] if voice_messages else []
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/prompt")
async def get_current_prompt():
    """Получить текущие инструкции бота для админ панели"""
    try:
        if AI_ENABLED and 'agent' in globals():
            instruction_data = agent.instruction
            return {
                "status": "success",
                "ai_enabled": True,
                "system_instruction": instruction_data.get("system_instruction", ""),
                "welcome_message": instruction_data.get("welcome_message", ""),
                "last_updated": instruction_data.get("last_updated", "неизвестно"),
                "instruction_length": len(instruction_data.get("system_instruction", "")),
                "agent_status": {
                    "openai_client": "configured" if agent.openai_client else "missing",
                    "zep_client": "configured" if agent.zep_client else "missing"
                }
            }
        else:
            return {
                "status": "success",
                "ai_enabled": False,
                "error": "AI agent не загружен"
            }
    except Exception as e:
        return {"error": str(e)}

@app.post("/admin/reload-prompt")
async def reload_prompt():
    """Перезагрузить инструкции бота"""
    try:
        if AI_ENABLED and 'agent' in globals():
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

@app.post("/webhook")
async def process_webhook(request: Request):
    """Главный обработчик webhook"""
    global update_counter
    try:
        # Проверяем secret token из заголовков
        secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret_token != WEBHOOK_SECRET_TOKEN:
            logger.warning(f"❌ Неверный secret token: {secret_token}")
            return {"ok": False, "error": "Invalid secret token"}
        
        json_data = await request.body()
        json_string = json_data.decode('utf-8')
        
        logger.info(f"📨 Webhook получен: {json_string[:150]}...")
        print(f"📨 Обработка webhook update...")
        
        update_dict = json.loads(json_string)
        
        # Сохраняем update для отладки
        update_counter += 1
        debug_update = {
            "id": update_counter,
            "timestamp": datetime.now().isoformat(),
            "type": "unknown",
            "data": update_dict
        }
        
        # Определяем тип update
        if "message" in update_dict:
            debug_update["type"] = "message"
        elif "business_message" in update_dict:
            debug_update["type"] = "business_message"
        elif "business_connection" in update_dict:
            debug_update["type"] = "business_connection"
        elif "edited_business_message" in update_dict:
            debug_update["type"] = "edited_business_message"
        elif "deleted_business_messages" in update_dict:
            debug_update["type"] = "deleted_business_messages"
        else:
            debug_update["type"] = f"other: {list(update_dict.keys())}"
            
        last_updates.append(debug_update)
        logger.info(f"📊 Update #{update_counter} тип: {debug_update['type']}")
        
        # Structured logging для webhook
        if STRUCTURED_LOGGING:
            try:
                log_webhook_received(
                    update_type=debug_update["type"],
                    user_id="system",
                    user_name="webhook",
                    message_type=debug_update["type"],
                    update_counter=update_counter
                )
            except Exception as struct_log_error:
                logger.warning(f"⚠️ Structured logging error: {struct_log_error}")
        
        # === ОБЫЧНЫЕ СООБЩЕНИЯ ===
        if "message" in update_dict:
            msg = update_dict["message"]
            chat_id = msg["chat"]["id"]
            text = msg.get("text", "") or msg.get("caption", "")
            user_id = msg.get("from", {}).get("id", "unknown")
            user_name = msg.get("from", {}).get("first_name", "Пользователь")
            
            # 🎤 РАСШИРЕННОЕ ЛОГИРОВАНИЕ ДЛЯ VOICE MESSAGES
            message_type = "text"
            if "voice" in msg:
                message_type = "voice"
                voice_info = msg["voice"]
                duration = voice_info.get('duration', 0)
                file_size = voice_info.get('file_size', 0)
                file_id = voice_info.get('file_id', 'unknown')
                
                logger.info(f"🎤 VOICE MESSAGE получено от {user_name} (ID: {user_id})")
                logger.info(f"   Длительность: {duration}s")
                logger.info(f"   Размер файла: {file_size} bytes")
                logger.info(f"   File ID: {file_id}")
                
                # Structured logging для voice message
                if STRUCTURED_LOGGING:
                    try:
                        log_voice_message(
                            user_id=str(user_id),
                            user_name=user_name,
                            duration=duration,
                            file_size=file_size,
                            processed=AI_ENABLED,
                            file_id=file_id
                        )
                    except Exception as struct_error:
                        logger.warning(f"⚠️ Structured logging error for voice: {struct_error}")
                
                if not AI_ENABLED:
                    logger.warning(f"⚠️ AI отключен - voice message НЕ БУДЕТ ОБРАБОТАНО!")
            elif "audio" in msg:
                message_type = "audio"
                audio_info = msg["audio"]
                logger.info(f"🎵 AUDIO MESSAGE получено от {user_name}")
                logger.info(f"   Длительность: {audio_info.get('duration', 'unknown')}s")
            elif "video_note" in msg:
                message_type = "video_note"
                logger.info(f"🎥 VIDEO NOTE получено от {user_name}")
            elif "photo" in msg:
                message_type = "photo"
                logger.info(f"📷 PHOTO получено от {user_name}")
            elif "document" in msg:
                message_type = "document"
                logger.info(f"📄 DOCUMENT получено от {user_name}")
            elif text:
                logger.info(f"💬 TEXT MESSAGE от {user_name}: {text[:50]}...")
            
            try:
                # Пытаемся отправить индикатор набора текста
                try:
                    bot.send_chat_action(chat_id, 'typing')
                except Exception as typing_error:
                    logger.warning(f"⚠️ Не удалось отправить typing индикатор: {typing_error}")
                
                # Обрабатываем команды
                if text.startswith("/start"):
                    if AI_ENABLED:
                        response = agent.get_welcome_message()
                    else:
                        response = f"👋 Привет, {user_name}! Добро пожаловать в artemmyassyst бот!"
                
                elif text.startswith("/help"):
                    response = """ℹ️ Помощь:
/start - начать работу
/help - показать помощь

Просто напишите ваш вопрос, и я помогу!"""
                
                # Обработка voice messages
                elif message_type == "voice" and AI_ENABLED:
                    try:
                        logger.info(f"🎤 Начинаю обработку voice message от {user_name}")
                        
                        # Получаем файл голосового сообщения
                        voice_file_id = voice_info.get('file_id')
                        if not voice_file_id:
                            logger.error("❌ Не удалось получить file_id голосового сообщения")
                            response = f"Извините, {user_name}, не удалось получить голосовое сообщение."
                        else:
                            # Получаем информацию о файле
                            file_info = bot.get_file(voice_file_id)
                            file_path = file_info.file_path
                            
                            # Скачиваем файл
                            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
                            logger.info(f"🎤 Скачиваю голосовое сообщение: {file_url}")
                            
                            voice_response = requests.get(file_url, timeout=30)
                            if voice_response.status_code == 200:
                                # Сохраняем временный файл
                                temp_voice_path = f"temp_voice_{user_id}_{int(time.time())}.ogg"
                                with open(temp_voice_path, 'wb') as f:
                                    f.write(voice_response.content)
                                
                                logger.info(f"🎤 Файл сохранен: {temp_voice_path}")
                                
                                try:
                                    # Преобразуем голос в текст через OpenAI Whisper
                                    if agent.openai_client:
                                        logger.info("🎤 Преобразование голоса в текст через Whisper...")
                                        
                                        with open(temp_voice_path, 'rb') as audio_file:
                                            transcript = await agent.openai_client.audio.transcriptions.create(
                                                model="whisper-1",
                                                file=audio_file,
                                                language="ru"
                                            )
                                        
                                        transcribed_text = transcript.text
                                        logger.info(f"🎤 Текст распознан: {transcribed_text[:100]}...")
                                        
                                        if transcribed_text.strip():
                                            # Обрабатываем распознанный текст через AI
                                            session_id = f"user_{user_id}"
                                            if agent.zep_client:
                                                await agent.ensure_user_exists(f"user_{user_id}", {
                                                    'first_name': user_name,
                                                    'email': f'{user_id}@telegram.user'
                                                })
                                                await agent.ensure_session_exists(session_id, f"user_{user_id}")
                                            
                                            start_time = time.time()
                                            ai_response = await agent.generate_response(transcribed_text, session_id, user_name)
                                            response_time = time.time() - start_time
                                            
                                            response = f"🎤 Ваше сообщение: \"{transcribed_text}\"\n\n{ai_response}"
                                            
                                            # Structured logging для voice to AI response
                                            if STRUCTURED_LOGGING:
                                                try:
                                                    log_ai_response(
                                                        user_id=str(user_id),
                                                        user_name=user_name,
                                                        input_text=f"[VOICE] {transcribed_text}",
                                                        response_text=ai_response,
                                                        ai_enabled=True,
                                                        response_time=response_time,
                                                        session_id=session_id
                                                    )
                                                except Exception as struct_error:
                                                    logger.warning(f"⚠️ Structured logging error: {struct_error}")
                                            
                                            logger.info(f"✅ Voice message обработано успешно для {user_name}")
                                        else:
                                            response = f"🎤 Не удалось распознать речь в вашем сообщении, {user_name}. Попробуйте говорить четче или напишите текстом."
                                    else:
                                        response = f"🎤 {user_name}, обработка голосовых сообщений недоступна - не настроен OpenAI API ключ."
                                        
                                except Exception as whisper_error:
                                    logger.error(f"❌ Ошибка Whisper: {whisper_error}")
                                    response = f"Извините, {user_name}, не удалось распознать голосовое сообщение. Попробуйте написать текстом."
                                
                                finally:
                                    # Удаляем временный файл
                                    try:
                                        os.remove(temp_voice_path)
                                        logger.info(f"🗑️ Временный файл удален: {temp_voice_path}")
                                    except:
                                        pass
                            else:
                                logger.error(f"❌ Не удалось скачать голосовое сообщение: {voice_response.status_code}")
                                response = f"Извините, {user_name}, не удалось загрузить голосовое сообщение."
                                
                    except Exception as voice_error:
                        logger.error(f"❌ Ошибка обработки voice message: {voice_error}")
                        logger.error(f"Traceback:\n{traceback.format_exc()}")
                        response = f"Извините, {user_name}, произошла ошибка при обработке голосового сообщения. Попробуйте написать текстом."
                
                # Если есть текст - обрабатываем через AI
                elif text and AI_ENABLED:
                    try:
                        session_id = f"user_{user_id}"
                        # Создаем пользователя в Zep если нужно
                        if agent.zep_client:
                            await agent.ensure_user_exists(f"user_{user_id}", {
                                'first_name': user_name,
                                'email': f'{user_id}@telegram.user'
                            })
                            await agent.ensure_session_exists(session_id, f"user_{user_id}")
                        start_time = time.time()
                        response = await agent.generate_response(text, session_id, user_name)
                        response_time = time.time() - start_time
                        
                        # Structured logging для AI response
                        if STRUCTURED_LOGGING:
                            try:
                                log_ai_response(
                                    user_id=str(user_id),
                                    user_name=user_name,
                                    input_text=text,
                                    response_text=response,
                                    ai_enabled=True,
                                    response_time=response_time,
                                    session_id=session_id
                                )
                            except Exception as struct_error:
                                logger.warning(f"⚠️ Structured logging error for AI: {struct_error}")
                        
                    except Exception as ai_error:
                        logger.error(f"Ошибка AI генерации: {ai_error}")
                        
                        # Structured logging для ошибки
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
                        
                        response = f"Извините, произошла техническая ошибка. Попробуйте позже или напишите вопрос снова."
                    
                elif text:
                    # Fallback если AI не доступен
                    response = f"👋 {user_name}, получил ваш вопрос! Подготовлю ответ. Минуточку!\n\n⚠️ Внимание: AI временно недоступен, работаю в упрощенном режиме."
                elif message_type == "voice":
                    # Voice message без AI
                    response = f"🎤 {user_name}, получил ваше голосовое сообщение!\n\n⚠️ К сожалению, обработка голосовых сообщений недоступна из-за проблем с AI.\n\nПожалуйста, напишите ваш вопрос текстом."
                    logger.warning(f"⚠️ Voice message от {user_name} - AI недоступен, отправляю заглушку")
                else:
                    logger.info(f"ℹ️ Неподдерживаемый тип сообщения '{message_type}' от {user_name}")
                    return {"ok": True, "action": "no_action"}
                    
                # Отправляем ответ
                bot.send_message(chat_id, response)
                logger.info(f"✅ Ответ отправлен в чат {chat_id}")
                print(f"✅ Отправлен ответ пользователю {user_name}")
                
            except Exception as e:
                logger.error(f"Ошибка обработки сообщения: {e}")
                bot.send_message(chat_id, "Извините, произошла непредвиденная ошибка. Попробуйте написать снова.")
        
        # === BUSINESS СООБЩЕНИЯ ===
        elif "business_message" in update_dict:
            bus_msg = update_dict["business_message"]
            
            chat_id = bus_msg["chat"]["id"]
            text = bus_msg.get("text", "") or bus_msg.get("caption", "")
            user_id = bus_msg.get("from", {}).get("id", "unknown")
            business_connection_id = bus_msg.get("business_connection_id")
            user_name = bus_msg.get("from", {}).get("first_name", "Клиент")
            
            # 🚫 КРИТИЧНАЯ ПРОВЕРКА: Игнорируем сообщения от владельца аккаунта
            if business_connection_id and business_connection_id in business_owners:
                owner_id = business_owners[business_connection_id]
                if str(user_id) == str(owner_id):
                    logger.info(f"🚫 ИГНОРИРУЕМ сообщение от владельца аккаунта: {user_name} (ID: {user_id})")
                    return {"ok": True, "action": "ignored_owner_message", "reason": "message_from_business_owner"}
            
            # Обрабатываем business сообщения с текстом
            if text:
                try:
                    logger.info(f"🔄 Начинаю обработку business message: text='{text}', chat_id={chat_id}")
                    
                    if AI_ENABLED:
                        logger.info(f"🤖 AI включен, генерирую ответ...")
                        session_id = f"business_{user_id}"
                        # Создаем пользователя в Zep если нужно
                        if agent.zep_client:
                            await agent.ensure_user_exists(f"business_{user_id}", {
                                'first_name': user_name,
                                'email': f'{user_id}@business.telegram.user'
                            })
                            await agent.ensure_session_exists(session_id, f"business_{user_id}")
                        response = await agent.generate_response(text, session_id, user_name)
                        logger.info(f"✅ AI ответ сгенерирован: {response[:100]}...")
                    else:
                        logger.info(f"🤖 AI отключен, использую стандартный ответ")
                        response = f"👋 Здравствуйте, {user_name}! Получил ваш вопрос. Подготовлю ответ!"
                    
                    # Для business_message используем специальную функцию
                    logger.info(f"📤 Пытаюсь отправить ответ клиенту {user_name}...")
                    if business_connection_id:
                        result = send_business_message(chat_id, response, business_connection_id)
                        if result:
                            logger.info(f"✅ Business ответ отправлен клиенту в чат {chat_id}")
                        else:
                            logger.error(f"❌ Не удалось отправить через Business API")
                    else:
                        bot.send_message(chat_id, response)
                        logger.warning(f"⚠️ Отправлено как обычное сообщение (fallback)")
                    
                    print(f"✅ Business ответ отправлен клиенту {user_name}")
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка обработки business сообщения: {e}")
                    logger.error(f"Traceback:\n{traceback.format_exc()}")
                    
                    # ВАЖНО: Отправляем ошибку ТОЖЕ через Business API!
                    try:
                        error_message = "Извините, произошла техническая ошибка. Попробуйте написать снова."
                        
                        if business_connection_id:
                            result = send_business_message(chat_id, error_message, business_connection_id)
                            if result:
                                logger.info(f"✅ Сообщение об ошибке отправлено через Business API")
                            else:
                                bot.send_message(chat_id, error_message)
                                logger.warning(f"⚠️ Business API не сработал, отправлено обычным способом")
                        else:
                            bot.send_message(chat_id, error_message)
                            logger.warning(f"⚠️ Сообщение об ошибке отправлено БЕЗ Business API (нет connection_id)")
                            
                    except Exception as send_error:
                        logger.error(f"❌ Не удалось отправить сообщение об ошибке: {send_error}")
        
        # === BUSINESS CONNECTION ===
        elif "business_connection" in update_dict:
            conn = update_dict["business_connection"]
            is_enabled = conn.get("is_enabled", False)
            connection_id = conn.get("id")
            user_info = conn.get("user", {})
            user_name = user_info.get("first_name", "Пользователь")
            owner_user_id = user_info.get("id")
            
            # Сохраняем владельца Business Connection для фильтрации сообщений
            if connection_id and owner_user_id:
                if is_enabled:
                    business_owners[connection_id] = owner_user_id
                    logger.info(f"✅ Сохранен владелец Business Connection: {user_name} (ID: {owner_user_id}) для connection_id: {connection_id}")
                else:
                    business_owners.pop(connection_id, None)
                    logger.info(f"❌ Удален владелец Business Connection: {user_name} (connection_id: {connection_id})")
                
                # Structured logging для business connection
                if STRUCTURED_LOGGING:
                    try:
                        log_business_connection(
                            connection_id=connection_id,
                            user_id=str(owner_user_id),
                            user_name=user_name,
                            is_enabled=is_enabled
                        )
                    except Exception as struct_error:
                        logger.warning(f"⚠️ Structured logging error for business: {struct_error}")
            
            status = "✅ Подключен" if is_enabled else "❌ Отключен"
            logger.info(f"{status} к Business аккаунту: {user_name}")
            logger.info(f"📊 Всего активных Business Connection: {len(business_owners)}")
        
        return {"ok": True, "status": "processed", "update_id": update_counter}
        
    except Exception as e:
        logger.error(f"❌ Ошибка webhook: {e}")
        return {"ok": False, "error": str(e)}

@app.on_event("startup")
async def startup():
    """Запуск сервера"""
    print("\n" + "="*50)
    print("🚀 artemmyassyst BOT WEBHOOK SERVER")
    print("="*50)
    
    # Очищаем webhook при старте
    try:
        bot.delete_webhook()
        print("🧹 Webhook очищен")
    except:
        pass
    
    try:
        bot_info = bot.get_me()
        print(f"🤖 Бот: @{bot_info.username}")
        print(f"📊 ID: {bot_info.id}")
        print(f"📛 Имя: {bot_info.first_name}")
        print("🔗 Режим: WEBHOOK ONLY")
        print("❌ Polling: ОТКЛЮЧЕН")
        print(f"🤖 AI: {'✅ ВКЛЮЧЕН' if AI_ENABLED else '❌ ОТКЛЮЧЕН'}")
        openai_key = os.getenv('OPENAI_API_KEY')
        openai_configured = bool(openai_key)
        print(f"🔑 OpenAI API: {'✅ Настроен' if openai_configured else '❌ Не настроен'}")
        
        # Логируем проблему с API ключом если есть
        if not openai_configured and STRUCTURED_LOGGING:
            try:
                log_api_key_issue(
                    key_type="openai",
                    issue="API key not configured",
                    impact="AI responses disabled, using fallback stubs"
                )
            except Exception:
                pass
        elif openai_configured and len(openai_key) < 50 and STRUCTURED_LOGGING:
            try:
                log_api_key_issue(
                    key_type="openai",
                    issue="API key seems truncated",
                    key_length=len(openai_key),
                    expected_min_length=120
                )
            except Exception:
                pass
        print("="*50)
        logger.info("✅ Бот инициализирован успешно")
        
        # ВСЕГДА автоматически устанавливаем webhook при старте
        print("🔧 Автоматическая установка webhook...")
        try:
            webhook_url = os.getenv("WEBHOOK_URL", "https://artemassyst-bot-tt5dt.ondigitalocean.app/webhook")
            result = bot.set_webhook(
                url=webhook_url,
                secret_token=WEBHOOK_SECRET_TOKEN,
                allowed_updates=[
                    "message",
                    "business_connection", 
                    "business_message",
                    "edited_business_message",
                    "deleted_business_messages"
                ]
            )
            
            if result:
                print(f"✅ Webhook автоматически установлен: {webhook_url}")
                logger.info(f"✅ Webhook установлен при старте: {webhook_url}")
            else:
                print("❌ Не удалось установить webhook автоматически")
                logger.error("Ошибка автоматической установки webhook")
                
        except Exception as e:
            print(f"❌ Ошибка при автоматической установке webhook: {e}")
            logger.error(f"Ошибка автоустановки webhook: {e}")
            
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        logger.error(f"❌ Ошибка инициализации бота: {e}")

@app.on_event("shutdown")
async def shutdown():
    """Остановка сервера"""
    logger.info("🛑 Остановка artemmyassyst Bot Webhook Server")
    print("🛑 Сервер остановлен")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🌐 Запуск на порту {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)