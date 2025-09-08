"""
Конфигурация Google Sheets API
"""
import os
from typing import List

# OAuth2 настройки
SCOPES: List[str] = [
    'https://www.googleapis.com/auth/spreadsheets'
]

# Пути к файлам
CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'credentials', 'client_secret.json')
TOKEN_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'credentials', 'token.json')

# Настройки Google Sheets
SPREADSHEET_NAME = "Алена - CRM данные и аналитика"

# Структура листов
SHEET_CONFIGURATIONS = {
    'clients': {
        'name': 'Клиенты (Лиды)',
        'headers': [
            'ID сессии', 'Дата создания', 'Дата обновления', 'Имя', 'Телефон',
            'Telegram Username', 'WhatsApp', 'Город клиента', 'Находится в Сочи сейчас',
            'Дата прилёта', 'Местный житель', 'Цель покупки', 'Форма оплаты',
            'Банк', 'Нужно продать своё', 'Бюджет мин', 'Бюджет макс', 'Локации',
            'Тип объекта', 'Параметры', 'Опыт в Сочи', 'Срочность', 
            'Удалённая сделка', 'Готовность к онлайн-показу', 'Предпочтительные слоты',
            'Канал связи', 'Квалификация', 'Следующее действие', 'Назначенный менеджер',
            'UTM источник', 'Комментарии', 'Состояние диалога'
        ]
    },
    'events': {
        'name': 'Аналитика событий',
        'headers': [
            'Session ID', 'Тип события', 'Данные события', 'Временная метка'
        ]
    },
    'funnel': {
        'name': 'Воронка конверсии',
        'headers': [
            'Состояние', 'Количество', 'Процент конверсии', 'Дата расчёта'
        ]
    },
    'daily_stats': {
        'name': 'Ежедневная статистика',
        'headers': [
            'Дата', 'Общее количество событий', 'Уникальные сессии', 
            'Новые лиды', 'Горячие лиды', 'Эскалации'
        ]
    }
}

# Настройки синхронизации
DEFAULT_SYNC_INTERVAL = 3600  # 1 час в секундах
BATCH_SIZE = 100  # Размер пакета для пакетных операций

# Email для предоставления доступа к таблице
TARGET_EMAIL = "aleynikov.artem@gmail.com"