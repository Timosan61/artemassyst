#!/usr/bin/env python3
"""
Тестирование OAuth2 после исправления redirect URI в Google Cloud Console
"""

import json
import urllib.parse
import time

CREDENTIALS_FILE = 'credentials/client_secret.json'

def test_oauth_playground_url():
    print("🔍 ТЕСТИРОВАНИЕ OAUTH PLAYGROUND ПОСЛЕ ИСПРАВЛЕНИЯ")
    print("=" * 80)
    
    # Читаем credentials
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            config = json.load(f)
        client_id = config['installed']['client_id']
        client_secret = config['installed']['client_secret']
    except Exception as e:
        print(f"❌ Ошибка чтения credentials: {e}")
        return False
    
    print(f"✅ Client ID: {client_id[:30]}...")
    print(f"✅ Client Secret: {client_secret[:10]}...")
    print()
    
    # Генерируем OAuth URL для OAuth Playground
    redirect_uri = "https://developers.google.com/oauthplayground"
    scope = "https://www.googleapis.com/auth/spreadsheets"
    
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'response_type': 'code',
        'access_type': 'offline',
        'include_granted_scopes': 'true'
    }
    
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    query_string = urllib.parse.urlencode(params)
    oauth_url = f"{base_url}?{query_string}"
    
    print("🔗 OAuth URL для тестирования:")
    print("=" * 80)
    print(oauth_url)
    print("=" * 80)
    print()
    
    # Инструкции
    print("📋 ИНСТРУКЦИИ ДЛЯ ТЕСТИРОВАНИЯ:")
    print()
    print("1. 📥 СНАЧАЛА исправьте redirect URI в Google Cloud Console:")
    print("   - Откройте: https://console.cloud.google.com/apis/credentials")
    print(f"   - Найдите клиент: {client_id}")
    print("   - Добавьте URI: https://developers.google.com/oauthplayground")
    print("   - Сохраните изменения")
    print("   - Подождите 1-2 минуты")
    print()
    
    print("2. 🧪 ЗАТЕМ протестируйте OAuth URL:")
    print("   - Скопируйте URL выше")
    print("   - Откройте в браузере")
    print("   - Должен открыться экран авторизации Google (без ошибок)")
    print()
    
    print("3. 🎯 ЕСЛИ РАБОТАЕТ:")
    print("   - Авторизуйтесь")
    print("   - Получите authorization code")
    print("   - Запустите: python save_token.py [КОД]")
    print()
    
    print("4. ❌ ЕСЛИ НЕ РАБОТАЕТ:")
    print("   - Проверьте что redirect URI добавлен правильно")
    print("   - Подождите еще 2-3 минуты")
    print("   - Попробуйте снова")
    print()
    
    # Альтернативные варианты
    print("🔧 АЛЬТЕРНАТИВНЫЕ OAUTH PLAYGROUND НАСТРОЙКИ:")
    print()
    print("Настройки в OAuth Playground (https://developers.google.com/oauthplayground):")
    print("1. Нажмите на шестерёнку (Settings)")
    print("2. Отметьте 'Use your own OAuth credentials'")
    print(f"3. OAuth Client ID: {client_id}")
    print(f"4. OAuth Client secret: {client_secret}")
    print("5. Close settings")
    print("6. Выберите 'Google Sheets API v4'")
    print("7. Выберите scope: https://www.googleapis.com/auth/spreadsheets")
    print("8. Нажмите 'Authorize APIs'")
    print()
    
    return oauth_url

if __name__ == "__main__":
    test_oauth_playground_url()