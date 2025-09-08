#!/usr/bin/env python3
"""
Диагностика и исправление OAuth2 конфигурации Google Sheets
"""

import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials/client_secret.json'

def check_config():
    print("🔍 Диагностика OAuth2 конфигурации Google Sheets")
    print("=" * 60)
    
    # 1. Проверяем файл учетных данных
    if not os.path.exists(CREDENTIALS_FILE):
        print("❌ Файл учетных данных не найден!")
        print("📋 Создайте OAuth2 клиент в Google Cloud Console:")
        print("   1. https://console.cloud.google.com/apis/credentials")
        print("   2. Create Credentials > OAuth client ID")
        print("   3. Application type: Desktop application")
        print("   4. Download JSON file")
        return False
    
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")
        return False
    
    print("✅ Файл учетных данных найден")
    
    # 2. Проверяем структуру файла
    if 'installed' not in config:
        print("❌ Неправильная структура файла!")
        print("📋 Файл должен содержать секцию 'installed'")
        print("   Возможно, выбран неправильный тип приложения")
        print("   Используйте 'Desktop application', а не 'Web application'")
        return False
    
    installed = config['installed']
    client_id = installed.get('client_id', '')
    client_secret = installed.get('client_secret', '')
    
    print(f"✅ Структура файла корректна")
    print(f"   Client ID: {client_id[:30]}...")
    print(f"   Client Secret: {client_secret[:10]}...")
    
    # 3. Проверяем валидность учетных данных
    if 'YOUR_GOOGLE_CLIENT_ID_HERE' in client_id:
        print("❌ Файл содержит шаблонные значения!")
        print("📋 Замените на реальные учетные данные из Google Cloud Console")
        return False
    
    if not client_id.endswith('.apps.googleusercontent.com'):
        print("❌ Client ID имеет неправильный формат!")
        print("📋 Client ID должен заканчиваться на '.apps.googleusercontent.com'")
        return False
    
    if not client_secret.startswith('GOCSPX-'):
        print("❌ Client Secret имеет неправильный формат!")
        print("📋 Client Secret должен начинаться с 'GOCSPX-'")
        return False
    
    print("✅ Формат учетных данных корректен")
    
    # 4. Тестируем создание OAuth2 flow
    try:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        print("✅ OAuth2 flow создан успешно")
    except Exception as e:
        print(f"❌ Ошибка создания OAuth2 flow: {e}")
        return False
    
    print()
    print("🎉 Конфигурация OAuth2 корректна!")
    print()
    print("📋 Возможные причины ошибки авторизации:")
    print("1. Google Sheets API не включен в проекте")
    print("2. OAuth Consent Screen не настроен")
    print("3. Учетные данные созданы для другого типа приложения")
    print("4. Проект Google Cloud неактивен")
    print()
    print("🔧 Рекомендации:")
    print("1. Проверьте https://console.cloud.google.com/apis/library")
    print("   - Найдите 'Google Sheets API' и включите его")
    print("2. Настройте OAuth consent screen:")
    print("   - https://console.cloud.google.com/apis/credentials/consent")
    print("3. Убедитесь что клиент создан как 'Desktop application'")
    print("4. Попробуйте создать новые учетные данные")
    
    return True

def create_alternative_url():
    """Создает альтернативный URL для авторизации"""
    print()
    print("🔗 Альтернативный способ создания OAuth2 URL")
    print("=" * 60)
    
    client_id = "180368526577-6jim5getfupe7tj9uq915atqkbnkk4ju.apps.googleusercontent.com"
    scope = "https://www.googleapis.com/auth/spreadsheets"
    redirect_uri = "http://localhost"
    
    # Создаем URL вручную
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = [
        f"client_id={client_id}",
        f"redirect_uri={redirect_uri}",
        f"scope={scope}",
        "response_type=code",
        "access_type=offline",
        "include_granted_scopes=true"
    ]
    
    manual_url = f"{base_url}?" + "&".join(params)
    
    print("🌐 Ручной OAuth2 URL:")
    print(manual_url)
    print()
    print("📋 Если основной URL не работает, попробуйте этот")
    
    return manual_url

if __name__ == "__main__":
    success = check_config()
    create_alternative_url()
    
    if success:
        print()
        print("✅ Конфигурация готова к использованию!")
    else:
        print()
        print("❌ Требуется исправление конфигурации")