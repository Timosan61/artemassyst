#!/usr/bin/env python3
"""
Тестирование различных redirect_uri для OAuth2
"""

import json
import urllib.parse

CREDENTIALS_FILE = 'credentials/client_secret.json'

# Различные варианты redirect_uri которые могут быть настроены
REDIRECT_URIS = [
    "http://localhost",
    "http://localhost:8080", 
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "urn:ietf:wg:oauth:2.0:oob",  # Для desktop приложений (устаревший)
    "urn:ietf:wg:oauth:2.0:oob:auto",  # Автоматическое получение кода
    "https://localhost",
    "https://127.0.0.1"
]

def create_oauth_urls():
    # Читаем credentials
    with open(CREDENTIALS_FILE, 'r') as f:
        config = json.load(f)
    
    client_id = config['installed']['client_id']
    scope = "https://www.googleapis.com/auth/spreadsheets"
    
    print("🔍 Тестирование различных redirect_uri")
    print("=" * 80)
    print()
    
    for i, redirect_uri in enumerate(REDIRECT_URIS, 1):
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
        
        print(f"📍 Вариант {i}: redirect_uri = {redirect_uri}")
        print(f"   URL: {oauth_url}")
        print()
    
    print("=" * 80)
    print("📋 Инструкции:")
    print("1. Попробуйте каждый URL в браузере")
    print("2. Один из них должен работать с вашим проектом")
    print("3. Обычно для desktop приложений используется:")
    print("   - http://localhost (с портом или без)")
    print("   - urn:ietf:wg:oauth:2.0:oob (устаревший, но может работать)")
    print()
    print("🔧 Если ни один не работает:")
    print("1. Откройте https://console.cloud.google.com/apis/credentials")
    print("2. Найдите ваш OAuth 2.0 Client ID")
    print("3. Проверьте какие Authorized redirect URIs настроены")
    print("4. Добавьте 'http://localhost' в список разрешенных URI")

if __name__ == "__main__":
    create_oauth_urls()