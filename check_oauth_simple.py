#!/usr/bin/env python3
"""
Простая проверка OAuth2 конфигурации без внешних зависимостей
"""

import json
import os
import urllib.parse

CREDENTIALS_FILE = 'credentials/client_secret.json'

def create_oauth_url():
    print("🔍 Проверка OAuth2 конфигурации")
    print("=" * 60)
    
    # 1. Проверяем файл учетных данных
    if not os.path.exists(CREDENTIALS_FILE):
        print("❌ Файл учетных данных не найден!")
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
        return False
    
    installed = config['installed']
    client_id = installed.get('client_id', '')
    client_secret = installed.get('client_secret', '')
    
    print(f"✅ Структура файла корректна")
    print(f"   Client ID: {client_id[:30]}...")
    print(f"   Client Secret: {client_secret[:10]}...")
    
    # 3. Создаем OAuth2 URL вручную
    scope = "https://www.googleapis.com/auth/spreadsheets"
    redirect_uri = "http://localhost"
    
    # Параметры для OAuth2
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'response_type': 'code',
        'access_type': 'offline',
        'include_granted_scopes': 'true'
    }
    
    # Создаем URL
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    query_string = urllib.parse.urlencode(params)
    oauth_url = f"{base_url}?{query_string}"
    
    print()
    print("🔗 OAuth2 Authorization URL:")
    print("=" * 80)
    print(oauth_url)
    print("=" * 80)
    print()
    
    print("📋 Инструкции для получения authorization code:")
    print("1. Скопируйте URL выше")
    print("2. Откройте в браузере")
    print("3. Войдите как: aleynikov.artem@gmail.com")
    print("4. Разрешите доступ к Google Sheets")
    print("5. После перенаправления скопируйте код из URL")
    print("   (после 'code=' и до '&' или конца URL)")
    print("6. Запустите: python save_token.py [КОД]")
    print()
    
    print("🔧 Возможные проблемы:")
    print("1. Google Sheets API не включен в проекте")
    print("   - Перейдите: https://console.cloud.google.com/apis/library")
    print("   - Найдите 'Google Sheets API' и включите его")
    print("2. OAuth Consent Screen не настроен")
    print("   - Перейдите: https://console.cloud.google.com/apis/credentials/consent")
    print("   - Настройте экран согласия для приложения")
    print("3. Проект не активен или заблокирован")
    
    return oauth_url

if __name__ == "__main__":
    oauth_url = create_oauth_url()
    if oauth_url:
        print()
        print("✅ URL сгенерирован успешно!")
        print("📋 Попробуйте авторизацию по этому URL")
    else:
        print()
        print("❌ Ошибка генерации URL")