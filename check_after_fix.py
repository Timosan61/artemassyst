#!/usr/bin/env python3
"""
Проверка OAuth2 после добавления redirect URI
"""

import json
import urllib.parse
import requests
from datetime import datetime

CREDENTIALS_FILE = 'credentials/client_secret.json'

def test_oauth_urls():
    print("🧪 ПРОВЕРКА OAuth2 ПОСЛЕ ДОБАВЛЕНИЯ REDIRECT URI")
    print("=" * 80)
    print(f"⏰ Время проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            config = json.load(f)
        client_id = config['installed']['client_id']
        client_secret = config['installed']['client_secret']
    except Exception as e:
        print(f"❌ Ошибка чтения credentials: {e}")
        return
    
    print(f"🆔 Client ID: {client_id}")
    print(f"🔐 Client Secret: {client_secret[:15]}...")
    print()
    
    # Тест 1: OAuth Playground URL
    print("🧪 ТЕСТ 1: OAuth Playground URL")
    print("-" * 60)
    
    playground_params = {
        'client_id': client_id,
        'redirect_uri': 'https://developers.google.com/oauthplayground',
        'scope': 'https://www.googleapis.com/auth/spreadsheets',
        'response_type': 'code',
        'access_type': 'offline'
    }
    
    playground_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(playground_params)}"
    print(f"URL: {playground_url}")
    
    try:
        # Проверяем доступность URL (не следуем редиректам)
        response = requests.head(playground_url, allow_redirects=False, timeout=10)
        if response.status_code == 302:
            print("✅ OAuth Playground URL - РАБОТАЕТ (redirect 302)")
            print("   Можно использовать для авторизации")
        elif response.status_code == 400:
            print("❌ OAuth Playground URL - НЕ РАБОТАЕТ (400 error)")
            print("   Redirect URI еще не добавлен или не применился")
        else:
            print(f"⚠️ OAuth Playground URL - статус {response.status_code}")
    except Exception as e:
        print(f"⚠️ Ошибка проверки Playground URL: {e}")
    
    print()
    
    # Тест 2: Localhost URL  
    print("🧪 ТЕСТ 2: Localhost URL")
    print("-" * 60)
    
    localhost_params = {
        'client_id': client_id,
        'redirect_uri': 'http://localhost:8080',
        'scope': 'https://www.googleapis.com/auth/spreadsheets',
        'response_type': 'code', 
        'access_type': 'offline'
    }
    
    localhost_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(localhost_params)}"
    print(f"URL: {localhost_url}")
    
    try:
        response = requests.head(localhost_url, allow_redirects=False, timeout=10)
        if response.status_code == 302:
            print("✅ Localhost URL - РАБОТАЕТ (redirect 302)")
            print("   Можно использовать локальный сервер")
        elif response.status_code == 400:
            print("❌ Localhost URL - НЕ РАБОТАЕТ (400 error)")
            print("   Redirect URI еще не добавлен или не применился")
        else:
            print(f"⚠️ Localhost URL - статус {response.status_code}")
    except Exception as e:
        print(f"⚠️ Ошибка проверки Localhost URL: {e}")
    
    print()
    
    # Инструкции по результатам
    print("📋 ЧТО ДЕЛАТЬ ДАЛЬШЕ:")
    print("=" * 80)
    print("✅ Если оба теста РАБОТАЮТ:")
    print("   1. Запустите: python local_oauth_server.py")
    print("   2. Или используйте OAuth Playground")
    print("   3. Получите authorization code")
    print("   4. Запустите: python save_token.py [КОД]")
    print()
    
    print("❌ Если тесты НЕ РАБОТАЮТ:")
    print("   1. Проверьте что добавили redirect URI в Google Console")
    print("   2. Подождите еще 2-3 минуты")
    print("   3. Запустите этот скрипт снова")
    print("   4. Убедитесь что сохранили изменения в консоли")
    print()
    
    print("🔄 Запускайте этот скрипт каждые 2 минуты до получения ✅")

if __name__ == "__main__":
    test_oauth_urls()