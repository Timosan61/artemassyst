#!/usr/bin/env python3
"""
Инструкции для ручного исправления redirect_uri в Google Cloud Console
"""

import json

CREDENTIALS_FILE = 'credentials/client_secret.json'

def show_manual_instructions():
    print("🔧 РУЧНОЕ ИСПРАВЛЕНИЕ REDIRECT URI")
    print("=" * 80)
    
    # Читаем client_id
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            config = json.load(f)
        client_id = config['installed']['client_id']
    except Exception as e:
        print(f"❌ Ошибка чтения credentials: {e}")
        return
    
    print(f"📋 Ваш Client ID: {client_id}")
    print()
    
    # Шаги для исправления
    print("📍 ШАГИ ДЛЯ ИСПРАВЛЕНИЯ:")
    print()
    print("1. 🌐 Откройте в браузере:")
    print("   https://console.cloud.google.com/apis/credentials")
    print()
    print("2. 🔍 Найдите OAuth 2.0 Client ID:")
    print(f"   {client_id}")
    print()
    print("3. ✏️ Нажмите на клиент для редактирования")
    print()
    print("4. 📝 В разделе 'Authorized redirect URIs' добавьте:")
    print("   https://developers.google.com/oauthplayground")
    print()
    print("5. 💾 Нажмите 'Save'")
    print()
    
    print("=" * 80)
    print()
    print("📋 АЛЬТЕРНАТИВНЫЕ REDIRECT URI (добавьте все):")
    print("   • https://developers.google.com/oauthplayground")
    print("   • http://localhost")
    print("   • http://localhost:8080")
    print("   • http://127.0.0.1")
    print()
    
    print("⏳ ПОСЛЕ ДОБАВЛЕНИЯ URI:")
    print("1. Подождите 1-2 минуты для применения изменений")
    print("2. Вернитесь к OAuth Playground")
    print("3. Попробуйте авторизацию снова")
    print()
    
    print("🔗 OAuth Playground URL:")
    print("   https://developers.google.com/oauthplayground")
    print()
    
    print("📊 ЕСЛИ ВСЕ РАБОТАЕТ:")
    print("1. Выберите 'Google Sheets API v4'")
    print("2. Выберите scope: https://www.googleapis.com/auth/spreadsheets")
    print("3. Нажмите 'Authorize APIs'")
    print("4. Разрешите доступ")
    print("5. Получите authorization code")
    print("6. Запустите: python save_token.py [КОД]")

if __name__ == "__main__":
    show_manual_instructions()