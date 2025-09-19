"""
Менеджер сессий для вебхука с улучшенной логикой предотвращения повторов
"""
import time
import json
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from bot.memory.session_manager import session_manager

# Кэш сессий в памяти для быстрого доступа
session_cache = {}
SESSION_TTL = 24 * 60 * 60  # 24 часа

def get_or_create_session_id(user_id: str, chat_id: str, message_id: str) -> str:
    """
    Получает или создает уникальный session_id для Telegram сообщения

    Args:
        user_id: ID пользователя Telegram
        chat_id: ID чата Telegram
        message_id: ID сообщения Telegram

    Returns:
        Уникальный session_id
    """
    # Создаем уникальный ключ на основе user_id и chat_id
    cache_key = f"{user_id}_{chat_id}"

    # Проверяем кэш
    if cache_key in session_cache:
        session_info = session_cache[cache_key]
        # Проверяем TTL
        if time.time() - session_info['created_at'] < SESSION_TTL:
            return session_info['session_id']
        else:
            # Удаляем устаревшую сессию
            del session_cache[cache_key]

    # Создаем новую сессию
    session_id = session_manager.generate_session_id(user_id, chat_id)

    # Сохраняем в кэш
    session_cache[cache_key] = {
        'session_id': session_id,
        'user_id': user_id,
        'chat_id': chat_id,
        'created_at': time.time(),
        'last_message_id': message_id,
        'message_history': []
    }

    return session_id

def get_existing_session_id(user_id: str, chat_id: str) -> Optional[str]:
    """
    Получает существующий session_id без создания новой сессии

    Args:
        user_id: ID пользователя Telegram
        chat_id: ID чата Telegram

    Returns:
        session_id если существует, иначе None
    """
    cache_key = f"{user_id}_{chat_id}"

    if cache_key in session_cache:
        session_info = session_cache[cache_key]
        if time.time() - session_info['created_at'] < SESSION_TTL:
            return session_info['session_id']

    return None

def record_message_in_session(user_id: str, chat_id: str, message_id: str,
                            text: str, message_type: str):
    """
    Записывает сообщение в историю сессии для предотвращения дублирования

    Args:
        user_id: ID пользователя
        chat_id: ID чата
        message_id: ID сообщения
        text: Текст сообщения
        message_type: Тип сообщения (user/assistant)
    """
    cache_key = f"{user_id}_{chat_id}"

    if cache_key in session_cache:
        session_info = session_cache[cache_key]

        # Проверяем, не было ли уже такого сообщения
        for msg in session_info['message_history']:
            if msg['message_id'] == message_id:
                return False  # Сообщение уже обработано

        # Добавляем сообщение в историю
        session_info['message_history'].append({
            'message_id': message_id,
            'text': text,
            'type': message_type,
            'timestamp': time.time()
        })

        # Ограничиваем размер истории (последние 50 сообщений)
        if len(session_info['message_history']) > 50:
            session_info['message_history'] = session_info['message_history'][-50:]

        session_info['last_message_id'] = message_id
        return True

    return False

def is_duplicate_message(user_id: str, chat_id: str, message_id: str) -> bool:
    """
    Проверяет, было ли сообщение уже обработано

    Args:
        user_id: ID пользователя
        chat_id: ID чата
        message_id: ID сообщения

    Returns:
        True если сообщение уже обрабатывалось
    """
    cache_key = f"{user_id}_{chat_id}"

    if cache_key in session_cache:
        session_info = session_cache[cache_key]

        # Проверяем по ID сообщения
        for msg in session_info['message_history']:
            if msg['message_id'] == message_id:
                return True

    return False

def get_session_stats() -> dict:
    """Получает статистику по сессиям"""
    total_sessions = len(session_cache)
    active_sessions = sum(1 for info in session_cache.values()
                         if time.time() - info['created_at'] < SESSION_TTL)

    return {
        'total_sessions': total_sessions,
        'active_sessions': active_sessions,
        'session_ttl_hours': SESSION_TTL / 3600
    }

def cleanup_expired_sessions():
    """Очищает устаревшие сессии из кэша"""
    current_time = time.time()
    expired_keys = []

    for cache_key, session_info in session_cache.items():
        if current_time - session_info['created_at'] >= SESSION_TTL:
            expired_keys.append(cache_key)

    for cache_key in expired_keys:
        del session_cache[cache_key]

    return len(expired_keys)

# Функция для интеграции с вебхуком
def get_session_for_webhook(user_id: str, chat_id: str, message_id: str) -> tuple:
    """
    Универсальная функция для получения session_id для вебхука

    Returns:
        tuple: (session_id, existing_session_id)
    """
    # Проверяем на дубликат сообщения
    if is_duplicate_message(user_id, chat_id, message_id):
        return None, None

    # Получаем существующую сессию
    existing_session_id = get_existing_session_id(user_id, chat_id)

    # Создаем новую сессию или используем существующую
    session_id = get_or_create_session_id(user_id, chat_id, message_id)

    return session_id, existing_session_id

# Функция для обновления сессии после успешной обработки
def update_session_after_processing(user_id: str, chat_id: str, message_id: str,
                                  message_text: str, message_type: str):
    """Обновляет сессию после успешной обработки сообщения"""
    record_message_in_session(user_id, chat_id, message_id, message_text, message_type)

    # Обновляем активность сессии
    cache_key = f"{user_id}_{chat_id}"
    if cache_key in session_cache:
        session_info = session_cache[cache_key]
        session_manager.update_session_activity(session_info['session_id'])

if __name__ == "__main__":
    # Тестирование функций
    print("🧪 Тестирование session_manager_webhook...")

    # Создаем тестовую сессию
    session_id, existing_id = get_session_for_webhook("123456", "789", "100")
    print(f"📋 Создана сессия: {session_id}")
    print(f"📋 Существующая сессия: {existing_id}")

    # Проверяем дубликат
    is_dup = is_duplicate_message("123456", "789", "100")
    print(f"🔄 Дубликат сообщения: {is_dup}")

    # Статистика
    stats = get_session_stats()
    print(f"📊 Статистика: {stats}")

    print("✅ Тест завершен!")