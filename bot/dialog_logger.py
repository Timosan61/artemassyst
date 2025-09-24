"""
Система логирования диалогов для отслеживания и анализа взаимодействий
"""
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import asyncio
import threading
from collections import deque

logger = logging.getLogger(__name__)


class DialogLogger:
    """Логгер для сохранения всех диалогов с пользователями"""

    def __init__(self, log_dir: str = "logs/dialogs"):
        """
        Инициализация логгера диалогов

        Args:
            log_dir: Директория для сохранения логов диалогов
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Буфер для сообщений (чтобы не писать в файл каждое сообщение)
        self.message_buffer = deque(maxlen=100)
        self.buffer_lock = threading.Lock()

        # Последние диалоги в памяти для быстрого доступа
        self.recent_dialogs: Dict[str, List[Dict]] = {}
        self.max_recent_per_user = 50

        logger.info(f"✅ DialogLogger инициализирован. Логи в: {self.log_dir.absolute()}")

    def log_message(
        self,
        session_id: str,
        user_id: str,
        user_name: str,
        message_type: str,  # "user" или "assistant"
        text: str,
        state: Optional[str] = None,
        qualification: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Логирует сообщение в диалоге

        Args:
            session_id: ID сессии
            user_id: ID пользователя
            user_name: Имя пользователя
            message_type: Тип сообщения (user/assistant)
            text: Текст сообщения
            state: Текущее состояние диалога
            qualification: Статус квалификации
            metadata: Дополнительные метаданные
        """
        timestamp = datetime.now().isoformat()

        log_entry = {
            "timestamp": timestamp,
            "session_id": session_id,
            "user_id": user_id,
            "user_name": user_name,
            "message_type": message_type,
            "text": text,
            "state": state,
            "qualification": qualification,
            "metadata": metadata or {}
        }

        # Добавляем в буфер
        with self.buffer_lock:
            self.message_buffer.append(log_entry)

        # Сохраняем в recent_dialogs
        if user_id not in self.recent_dialogs:
            self.recent_dialogs[user_id] = []

        self.recent_dialogs[user_id].append(log_entry)

        # Ограничиваем количество сообщений в памяти
        if len(self.recent_dialogs[user_id]) > self.max_recent_per_user:
            self.recent_dialogs[user_id] = self.recent_dialogs[user_id][-self.max_recent_per_user:]

        # Если буфер полный, сбрасываем в файл
        if len(self.message_buffer) >= 10:
            self.flush_buffer()

    def log_state_transition(
        self,
        session_id: str,
        user_id: str,
        from_state: str,
        to_state: str,
        trigger_message: Optional[str] = None
    ) -> None:
        """
        Логирует переход между состояниями

        Args:
            session_id: ID сессии
            user_id: ID пользователя
            from_state: Исходное состояние
            to_state: Новое состояние
            trigger_message: Сообщение, вызвавшее переход
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "user_id": user_id,
            "transition": {
                "from": from_state,
                "to": to_state,
                "trigger": trigger_message
            }
        }

        # Записываем как специальное событие
        with self.buffer_lock:
            self.message_buffer.append(log_entry)

        logger.info(f"📊 Переход состояния: {from_state} -> {to_state} для сессии {session_id}")

    def flush_buffer(self) -> None:
        """Сбрасывает буфер сообщений в файл"""
        if not self.message_buffer:
            return

        # Определяем файл для текущего дня
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"dialogs_{today}.jsonl"

        with self.buffer_lock:
            messages_to_write = list(self.message_buffer)
            self.message_buffer.clear()

        try:
            # Записываем в JSONL формат (каждая строка - отдельный JSON)
            with open(log_file, "a", encoding="utf-8") as f:
                for message in messages_to_write:
                    f.write(json.dumps(message, ensure_ascii=False) + "\n")

            logger.debug(f"💾 Сохранено {len(messages_to_write)} сообщений в {log_file}")
        except Exception as e:
            logger.error(f"❌ Ошибка записи логов диалогов: {e}")

    def get_user_dialog(self, user_id: str, limit: int = 20) -> List[Dict]:
        """
        Получает последние сообщения пользователя из памяти

        Args:
            user_id: ID пользователя
            limit: Максимальное количество сообщений

        Returns:
            Список последних сообщений
        """
        if user_id not in self.recent_dialogs:
            return []

        return self.recent_dialogs[user_id][-limit:]

    def log_zep_data(
        self,
        session_id: str,
        user_id: str,
        operation: str,  # 'save' или 'load'
        zep_data: Dict
    ) -> None:
        """
        Логирует операции с данными ZEP

        Args:
            session_id: ID сессии
            user_id: ID пользователя
            operation: Тип операции (save/load)
            zep_data: Данные ZEP
        """
        timestamp = datetime.now().isoformat()

        log_entry = {
            "timestamp": timestamp,
            "session_id": session_id,
            "user_id": user_id,
            "message_type": f"zep_{operation}",
            "operation": operation,
            "zep_data": zep_data,
            "metadata": {
                "data_fields": list(zep_data.keys()) if zep_data else [],
                "data_size": len(str(zep_data)) if zep_data else 0
            }
        }

        # Добавляем в буфер
        with self.buffer_lock:
            self.message_buffer.append(log_entry)

        # Если буфер полный, сбрасываем в файл
        if len(self.message_buffer) >= 10:
            self.flush_buffer()

        logger.info(f"📊 ZEP {operation.upper()}: {session_id} - {len(zep_data) if zep_data else 0} полей")

    def get_all_recent_dialogs(self, limit: int = 100) -> List[Dict]:
        """
        Получает все последние диалоги

        Args:
            limit: Максимальное количество сообщений

        Returns:
            Список последних сообщений всех пользователей
        """
        all_messages = []

        for user_id, messages in self.recent_dialogs.items():
            all_messages.extend(messages)

        # Сортируем по времени
        all_messages.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return all_messages[:limit]

    def get_dialog_stats(self) -> Dict[str, Any]:
        """
        Получает статистику по диалогам

        Returns:
            Словарь со статистикой
        """
        total_users = len(self.recent_dialogs)
        total_messages = sum(len(msgs) for msgs in self.recent_dialogs.values())

        # Подсчет по состояниям
        state_counts = {}
        qualification_counts = {}

        for messages in self.recent_dialogs.values():
            for msg in messages:
                if msg.get("state"):
                    state_counts[msg["state"]] = state_counts.get(msg["state"], 0) + 1
                if msg.get("qualification"):
                    qualification_counts[msg["qualification"]] = qualification_counts.get(msg["qualification"], 0) + 1

        return {
            "total_users": total_users,
            "total_messages": total_messages,
            "states": state_counts,
            "qualifications": qualification_counts,
            "buffer_size": len(self.message_buffer)
        }

    def search_dialogs(self, query: str, user_id: Optional[str] = None) -> List[Dict]:
        """
        Поиск в диалогах

        Args:
            query: Поисковый запрос
            user_id: Ограничить поиск по пользователю

        Returns:
            Найденные сообщения
        """
        results = []
        query_lower = query.lower()

        if user_id and user_id in self.recent_dialogs:
            messages_to_search = self.recent_dialogs[user_id]
        else:
            messages_to_search = []
            for msgs in self.recent_dialogs.values():
                messages_to_search.extend(msgs)

        for msg in messages_to_search:
            if query_lower in msg.get("text", "").lower():
                results.append(msg)

        return results[:50]  # Ограничиваем результаты

    def export_user_dialog(self, user_id: str, format: str = "json") -> Optional[str]:
        """
        Экспортирует диалог пользователя

        Args:
            user_id: ID пользователя
            format: Формат экспорта (json, txt)

        Returns:
            Экспортированные данные или None
        """
        if user_id not in self.recent_dialogs:
            return None

        messages = self.recent_dialogs[user_id]

        if format == "json":
            return json.dumps(messages, ensure_ascii=False, indent=2)

        elif format == "txt":
            lines = []
            for msg in messages:
                timestamp = msg.get("timestamp", "")
                msg_type = msg.get("message_type", "")
                text = msg.get("text", "")
                state = msg.get("state", "")

                prefix = "👤 USER" if msg_type == "user" else "🤖 BOT"
                lines.append(f"[{timestamp}] {prefix}: {text}")
                if state:
                    lines.append(f"  📍 Состояние: {state}")

            return "\n".join(lines)

        return None

    def cleanup_old_logs(self, days_to_keep: int = 7) -> None:
        """
        Удаляет старые лог-файлы

        Args:
            days_to_keep: Количество дней для хранения логов
        """
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 86400)

        for log_file in self.log_dir.glob("dialogs_*.jsonl"):
            if log_file.stat().st_mtime < cutoff_date:
                try:
                    log_file.unlink()
                    logger.info(f"🗑️ Удален старый лог-файл: {log_file.name}")
                except Exception as e:
                    logger.error(f"❌ Ошибка удаления лог-файла {log_file.name}: {e}")

    def __del__(self):
        """Сброс буфера при уничтожении объекта"""
        try:
            self.flush_buffer()
        except:
            pass


# Глобальный экземпляр логгера диалогов
dialog_logger = DialogLogger()