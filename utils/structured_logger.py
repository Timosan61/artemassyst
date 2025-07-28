#!/usr/bin/env python3
"""
📊 Structured Logging System для artemassyst
Добавляет JSON-структурированное логирование с метаданными
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class StructuredLogger:
    def __init__(self, name: str = "artemassyst", log_file: str = "logs/structured.log"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Создаем директорию для логов
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # JSON formatter
        formatter = logging.Formatter('%(message)s')
        
        # File handler для структурированных логов
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # Добавляем handler
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
    
    def _create_log_entry(self, level: LogLevel, message: str, 
                         event_type: str = "general", **kwargs) -> Dict[str, Any]:
        """Создает структурированную запись лога"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.value,
            "message": message,
            "event_type": event_type,
            "service": "artemassyst",
            "metadata": kwargs
        }
        return entry
    
    def log_webhook_received(self, update_type: str, user_id: str, 
                           user_name: str, message_type: str = "text", **kwargs):
        """Логирование получения webhook"""
        entry = self._create_log_entry(
            LogLevel.INFO,
            f"Webhook received: {update_type}",
            "webhook_received",
            update_type=update_type,
            user_id=user_id,
            user_name=user_name,
            message_type=message_type,
            **kwargs
        )
        self.logger.info(json.dumps(entry, ensure_ascii=False))
    
    def log_ai_response(self, user_id: str, user_name: str, 
                       input_text: str, response_text: str, 
                       ai_enabled: bool, response_time: float = None, **kwargs):
        """Логирование AI ответа"""
        entry = self._create_log_entry(
            LogLevel.INFO,
            f"AI response generated for user {user_name}",
            "ai_response",
            user_id=user_id,
            user_name=user_name,
            input_length=len(input_text),
            response_length=len(response_text),
            ai_enabled=ai_enabled,
            response_time=response_time,
            **kwargs
        )
        self.logger.info(json.dumps(entry, ensure_ascii=False))
    
    def log_voice_message(self, user_id: str, user_name: str, 
                         duration: int, file_size: int, processed: bool, **kwargs):
        """Специальное логирование для голосовых сообщений"""
        entry = self._create_log_entry(
            LogLevel.INFO,
            f"Voice message from {user_name}",
            "voice_message",
            user_id=user_id,
            user_name=user_name,
            duration=duration,
            file_size=file_size,
            processed=processed,
            **kwargs
        )
        self.logger.info(json.dumps(entry, ensure_ascii=False))
    
    def log_error(self, error_type: str, error_message: str, 
                 user_id: str = None, **kwargs):
        """Логирование ошибок"""
        entry = self._create_log_entry(
            LogLevel.ERROR,
            f"Error occurred: {error_type}",
            "error",
            error_type=error_type,
            error_message=error_message,
            user_id=user_id,
            **kwargs
        )
        self.logger.error(json.dumps(entry, ensure_ascii=False))
    
    def log_business_connection(self, connection_id: str, user_id: str, 
                              user_name: str, is_enabled: bool, **kwargs):
        """Логирование Business API connections"""
        entry = self._create_log_entry(
            LogLevel.INFO,
            f"Business connection {'enabled' if is_enabled else 'disabled'}",
            "business_connection",
            connection_id=connection_id,
            user_id=user_id,
            user_name=user_name,
            is_enabled=is_enabled,
            **kwargs
        )
        self.logger.info(json.dumps(entry, ensure_ascii=False))
    
    def log_api_key_issue(self, key_type: str, issue: str, **kwargs):
        """Логирование проблем с API ключами"""
        entry = self._create_log_entry(
            LogLevel.WARNING,
            f"API key issue: {key_type} - {issue}",
            "api_key_issue",
            key_type=key_type,
            issue=issue,
            **kwargs
        )
        self.logger.warning(json.dumps(entry, ensure_ascii=False))
    
    def log_performance_metric(self, operation: str, duration: float, 
                             success: bool, **kwargs):
        """Логирование метрик производительности"""
        entry = self._create_log_entry(
            LogLevel.INFO,
            f"Performance metric: {operation}",
            "performance",
            operation=operation,
            duration=duration,
            success=success,
            **kwargs
        )
        self.logger.info(json.dumps(entry, ensure_ascii=False))

# Глобальный экземпляр для использования в приложении
structured_logger = StructuredLogger()

# Convenience functions
def log_webhook_received(update_type: str, user_id: str, user_name: str, 
                        message_type: str = "text", **kwargs):
    structured_logger.log_webhook_received(update_type, user_id, user_name, 
                                         message_type, **kwargs)

def log_ai_response(user_id: str, user_name: str, input_text: str, 
                   response_text: str, ai_enabled: bool, response_time: float = None, **kwargs):
    structured_logger.log_ai_response(user_id, user_name, input_text, 
                                    response_text, ai_enabled, response_time, **kwargs)

def log_voice_message(user_id: str, user_name: str, duration: int, 
                     file_size: int, processed: bool, **kwargs):
    structured_logger.log_voice_message(user_id, user_name, duration, 
                                      file_size, processed, **kwargs)

def log_error(error_type: str, error_message: str, user_id: str = None, **kwargs):
    structured_logger.log_error(error_type, error_message, user_id, **kwargs)

def log_business_connection(connection_id: str, user_id: str, user_name: str, 
                          is_enabled: bool, **kwargs):
    structured_logger.log_business_connection(connection_id, user_id, user_name, 
                                            is_enabled, **kwargs)

def log_api_key_issue(key_type: str, issue: str, **kwargs):
    structured_logger.log_api_key_issue(key_type, issue, **kwargs)

def log_performance_metric(operation: str, duration: float, success: bool, **kwargs):
    structured_logger.log_performance_metric(operation, duration, success, **kwargs)