#!/usr/bin/env python3
"""
Тест создания Google таблицы после OAuth2 авторизации
"""

import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TOKEN_FILE = 'credentials/token.json'

def test_sheets():
    # Проверяем токен
    if not os.path.exists(TOKEN_FILE):
        print(f"❌ Токен не найден: {TOKEN_FILE}")
        print("🔧 Сначала выполните OAuth2 авторизацию")
        return False
    
    try:
        # Загружаем токен
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
        if not creds.valid:
            print("❌ Токен недействителен")
            return False
        
        print("✅ Токен загружен и валиден")
        
        # Создаем сервис
        service = build('sheets', 'v4', credentials=creds)
        
        # Информация о пользователе
        drive_service = build('drive', 'v3', credentials=creds)
        about = drive_service.about().get(fields="user").execute()
        user = about.get('user', {})
        
        print(f"👤 Авторизован: {user.get('displayName', 'Unknown')}")
        print(f"📧 Email: {user.get('emailAddress', 'Unknown')}")
        
        # Создаем тестовую таблицу
        spreadsheet = {
            'properties': {
                'title': 'Алена - CRM данные и аналитика',
                'locale': 'ru_RU',
                'timeZone': 'Europe/Moscow'
            },
            'sheets': [
                {
                    'properties': {
                        'title': 'Клиенты (Лиды)',
                        'gridProperties': {'rowCount': 1000, 'columnCount': 32}
                    }
                },
                {
                    'properties': {
                        'title': 'Аналитика событий',
                        'gridProperties': {'rowCount': 1000, 'columnCount': 4}
                    }
                },
                {
                    'properties': {
                        'title': 'Воронка конверсии',
                        'gridProperties': {'rowCount': 100, 'columnCount': 4}
                    }
                },
                {
                    'properties': {
                        'title': 'Ежедневная статистика',
                        'gridProperties': {'rowCount': 365, 'columnCount': 6}
                    }
                }
            ]
        }
        
        result = service.spreadsheets().create(body=spreadsheet).execute()
        spreadsheet_id = result['spreadsheetId']
        url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        
        print()
        print("🎉 Google таблица создана успешно!")
        print(f"📊 ID: {spreadsheet_id}")
        print(f"🔗 URL: {url}")
        print()
        
        # Добавим заголовки для листа "Клиенты"
        headers = [
            'ID сессии', 'Дата создания', 'Дата обновления', 'Имя', 'Телефон',
            'Telegram Username', 'WhatsApp', 'Город клиента', 'Находится в Сочи сейчас',
            'Дата прилёта', 'Местный житель', 'Цель покупки', 'Форма оплаты',
            'Банк', 'Нужно продать своё', 'Бюджет мин', 'Бюджет макс',
            'Локации', 'Тип объекта', 'Параметры', 'Опыт в Сочи',
            'Срочность', 'Удалённая сделка', 'Готовность к онлайн-показу',
            'Предпочтительные слоты', 'Канал связи', 'Квалификация',
            'Следующее действие', 'Назначенный менеджер', 'UTM источник',
            'Комментарии', 'Состояние диалога'
        ]
        
        body = {'values': [headers]}
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Клиенты (Лиды)!A1:AF1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print("✅ Заголовки добавлены в лист 'Клиенты (Лиды)'")
        
        # Форматирование заголовков
        requests = [{
            'repeatCell': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': 0,
                    'endRowIndex': 1,
                    'startColumnIndex': 0,
                    'endColumnIndex': len(headers)
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9},
                        'textFormat': {'bold': True}
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat)'
            }
        }]
        
        batch_request = {'requests': requests}
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=batch_request
        ).execute()
        
        print("✅ Заголовки отформатированы")
        
        print()
        print("🚀 Google Sheets интеграция готова!")
        print("📋 Теперь можете:")
        print("1. Запустить бота с GOOGLE_SHEETS_ENABLED=true")
        print("2. Проверить статус: GET /admin/sheets/status")
        print("3. Запустить синхронизацию: POST /admin/sheets/sync")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_sheets()