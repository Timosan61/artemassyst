"""
Менеджер сессий для предотвращения конфликтов и повторяющихся вопросов
"""
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """Управление сессиями для предотвращения конфликтов памяти"""

    def __init__(self):
        # Кэш активных сессий в памяти
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        # Время жизни сессии по умолчанию (24 часа)
        self.session_ttl = 24 * 60 * 60

    def generate_session_id(self, user_id: str, chat_id: Optional[str] = None) -> str:
        """
        Генерирует уникальный session_id на основе user_id и времени

        Args:
            user_id: ID пользователя Telegram
            chat_id: ID чата (для групповых чатов)

        Returns:
            Уникальный session_id в формате: user_timestamp_uuid
        """
        timestamp = int(time.time())
        unique_part = uuid.uuid4().hex[:8]

        # Базовый session_id
        base_id = f"{user_id}_{timestamp}_{unique_part}"

        # Для групповых чатов добавляем chat_id
        if chat_id and chat_id != user_id:
            base_id = f"group_{chat_id}_{base_id}"

        # Сохраняем информацию о сессии
        self.active_sessions[base_id] = {
            'user_id': user_id,
            'chat_id': chat_id,
            'created_at': timestamp,
            'last_activity': timestamp,
            'question_history': set(),  # История заданных вопросов
            'data_collected': {}  # Собранные данные для быстрого доступа
        }

        logger.info(f"✅ Создана новая сессия: {base_id} для пользователя {user_id}")
        return base_id

    def get_or_create_session(self, user_id: str, chat_id: Optional[str] = None,
                            existing_session_id: Optional[str] = None) -> str:
        """
        Получает существующую сессию или создает новую

        Args:
            user_id: ID пользователя
            chat_id: ID чата
            existing_session_id: Существующий session_id (если есть)

        Returns:
            session_id для использования
        """
        # Если есть существующая сессия и она активна
        if existing_session_id and self.is_session_active(existing_session_id):
            self.update_session_activity(existing_session_id)
            logger.info(f"📋 Используется существующая сессия: {existing_session_id}")
            return existing_session_id

        # Создаем новую сессию
        new_session_id = self.generate_session_id(user_id, chat_id)
        logger.info(f"🆕 Создана новая сессия для пользователя {user_id}")
        return new_session_id

    def is_session_active(self, session_id: str) -> bool:
        """Проверяет активна ли сессия"""
        if session_id not in self.active_sessions:
            return False

        session_data = self.active_sessions[session_id]
        current_time = int(time.time())

        # Проверяем TTL
        if current_time - session_data['last_activity'] > self.session_ttl:
            # Удаляем устаревшую сессию
            del self.active_sessions[session_id]
            logger.info(f"🗑️ Удалена устаревшая сессия: {session_id}")
            return False

        return True

    def update_session_activity(self, session_id: str):
        """Обновляет время последней активности сессии"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['last_activity'] = int(time.time())

    def record_asked_question(self, session_id: str, question: str):
        """Записывает заданный вопрос для предотвращения повторов"""
        if session_id in self.active_sessions:
            # Нормализуем вопрос для сравнения
            normalized_question = self._normalize_question(question)
            self.active_sessions[session_id]['question_history'].add(normalized_question)
            logger.debug(f"📝 Записан вопрос в историю сессии {session_id}: {normalized_question}")

    def was_question_asked(self, session_id: str, question: str) -> bool:
        """Проверялся ли уже этот вопрос в текущей сессии"""
        if session_id not in self.active_sessions:
            return False

        normalized_question = self._normalize_question(question)
        was_asked = normalized_question in self.active_sessions[session_id]['question_history']

        if was_asked:
            logger.info(f"⚠️ Вопрос уже задавался в сессии {session_id}: {normalized_question}")

        return was_asked

    def record_collected_data(self, session_id: str, data_type: str, value: Any):
        """Записывает собранные данные для быстрой проверки"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['data_collected'][data_type] = value
            logger.debug(f"📊 Записаны данные {data_type} в сессию {session_id}")

    def has_collected_data(self, session_id: str, data_type: str) -> bool:
        """Проверяет наличие собранных данных определенного типа"""
        if session_id not in self.active_sessions:
            return False

        has_data = data_type in self.active_sessions[session_id]['data_collected']

        if has_data:
            logger.debug(f"✅ Данные {data_type} уже собраны в сессии {session_id}")

        return has_data

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получает информацию о сессии"""
        return self.active_sessions.get(session_id)

    def cleanup_expired_sessions(self):
        """Очищает устаревшие сессии"""
        current_time = int(time.time())
        expired_sessions = []

        for session_id, session_data in self.active_sessions.items():
            if current_time - session_data['last_activity'] > self.session_ttl:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.active_sessions[session_id]
            logger.info(f"🧹 Очищена устаревшая сессия: {session_id}")

    def _normalize_question(self, question: str) -> str:
        """Нормализует вопрос для сравнения"""
        # Приводим к нижнему регистру, удаляем лишние пробелы и знаки препинания
        normalized = question.lower().strip()

        # Удаляем common words that don't affect meaning
        stop_words = {'для', 'или', 'как', 'вы', 'сейчас', 'в', 'на', 'по'}
        words = normalized.split()
        filtered_words = [word for word in words if word not in stop_words]

        return ' '.join(filtered_words)

    def get_session_stats(self) -> Dict[str, Any]:
        """Получает статистику по сессиям"""
        total_sessions = len(self.active_sessions)

        if total_sessions == 0:
            return {
                'total_sessions': 0,
                'active_sessions': 0,
                'avg_questions_per_session': 0
            }

        total_questions = sum(
            len(session['question_history'])
            for session in self.active_sessions.values()
        )

        return {
            'total_sessions': total_sessions,
            'active_sessions': total_sessions,  # Все в active_sessions считаются активными
            'avg_questions_per_session': total_questions / total_sessions,
            'oldest_session': min(
                session['created_at']
                for session in self.active_sessions.values()
            ),
            'newest_session': max(
                session['created_at']
                for session in self.active_sessions.values()
            )
        }


# Глобальный экземпляр менеджера сессий
session_manager = SessionManager()