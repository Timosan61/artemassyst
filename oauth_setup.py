#!/usr/bin/env python3
"""
Простая OAuth2 авторизация для Google Sheets
"""

import os
import asyncio
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Настройки
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials/client_secret.json'
TOKEN_FILE = 'credentials/token.json'

def authenticate():
    """OAuth2 авторизация"""
    creds = None
    
    # Проверяем существующий токен
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # Если нет валидного токена
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Обновляю истекший токен...")
            creds.refresh(Request())
            print("✅ Токен обновлен")
        else:
            print("🆕 Запускаю новую OAuth2 авторизацию...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            
            # Попробуем локальный сервер
            try:
                creds = flow.run_local_server(port=0, open_browser=False)
                print("✅ OAuth2 авторизация завершена через локальный сервер")
            except Exception as e:
                print(f"⚠️ Локальный сервер недоступен: {e}")
                # Используем консольный режим
                print("📋 Переход к ручному режиму авторизации...")
                
                flow.redirect_uri = 'http://localhost'
                auth_url, _ = flow.authorization_url(
                    access_type='offline',
                    include_granted_scopes='true'
                )
                
                print(f"\n🔗 Откройте эту ссылку в браузере:")
                print(f"{auth_url}\n")
                print("📋 После авторизации скопируйте authorization code из URL")
                
                auth_code = input("Введите authorization code: ").strip()
                flow.fetch_token(code=auth_code)
                creds = flow.credentials
                print("✅ Ручная авторизация завершена")
        
        # Сохраняем токен
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        print(f"💾 Токен сохранен в {TOKEN_FILE}")
    
    return creds

def test_api_access(creds):
    """Тестируем доступ к API"""
    try:
        # Создаем сервис
        service = build('sheets', 'v4', credentials=creds)
        
        # Тестируем доступ через Drive API
        drive_service = build('drive', 'v3', credentials=creds)
        about = drive_service.about().get(fields="user").execute()
        user = about.get('user', {})
        
        print(f"👤 Авторизован как: {user.get('displayName', 'Unknown')}")
        print(f"📧 Email: {user.get('emailAddress', 'Unknown')}")
        
        return service
        
    except Exception as e:
        print(f"❌ Ошибка доступа к API: {e}")
        return None

def create_test_spreadsheet(service):
    """Создаем тестовую таблицу"""
    try:
        spreadsheet = {
            'properties': {
                'title': 'Алена - CRM данные (Тест)',
                'locale': 'ru_RU',
                'timeZone': 'Europe/Moscow'
            },
            'sheets': [{
                'properties': {
                    'title': 'Тест',
                    'gridProperties': {
                        'rowCount': 10,
                        'columnCount': 5
                    }
                }
            }]
        }
        
        result = service.spreadsheets().create(body=spreadsheet).execute()
        spreadsheet_id = result['spreadsheetId']
        url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        
        print(f"✅ Тестовая таблица создана!")
        print(f"📊 ID: {spreadsheet_id}")
        print(f"🔗 URL: {url}")
        
        # Добавим тестовые данные
        values = [
            ['Имя', 'Телефон', 'Город', 'Цель', 'Бюджет'],
            ['Тест Иванов', '+7 900 123 45 67', 'Москва', 'Инвестиции', '10 млн']
        ]
        
        body = {'values': values}
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Тест!A1:E2',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print("✅ Тестовые данные добавлены")
        
        return spreadsheet_id, url
        
    except Exception as e:
        print(f"❌ Ошибка создания таблицы: {e}")
        return None, None

def main():
    print("🚀 OAuth2 авторизация для Google Sheets API")
    print("=" * 50)
    
    # Проверяем файл учетных данных
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ Файл {CREDENTIALS_FILE} не найден!")
        print("📋 Создайте файл с OAuth2 учетными данными Google")
        return
    
    try:
        # Авторизация
        creds = authenticate()
        if not creds:
            print("❌ Не удалось получить учетные данные")
            return
        
        # Тест API
        service = test_api_access(creds)
        if not service:
            print("❌ Не удалось подключиться к API")
            return
        
        # Создаем тестовую таблицу
        spreadsheet_id, url = create_test_spreadsheet(service)
        
        print("\n" + "=" * 50)
        print("🎉 OAuth2 авторизация завершена успешно!")
        
        if spreadsheet_id:
            print(f"📊 Google таблица готова: {url}")
            print("✅ Интеграция Google Sheets готова к использованию")
        
        print("\n📋 Следующие шаги:")
        print("1. Убедитесь что GOOGLE_SHEETS_ENABLED=true в .env")
        print("2. Перезапустите бота")
        print("3. Проверьте статус: GET /admin/sheets/status")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()