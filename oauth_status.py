#!/usr/bin/env python3
"""
Проверка статуса OAuth2 интеграции
"""

import os
import json

def check_oauth_status():
    print("🔍 СТАТУС OAuth2 ИНТЕГРАЦИИ")
    print("=" * 80)
    
    # Проверяем credentials
    creds_file = 'credentials/client_secret.json'
    if os.path.exists(creds_file):
        print("✅ Файл credentials найден")
        try:
            with open(creds_file, 'r') as f:
                config = json.load(f)
            client_id = config['installed']['client_id']
            print(f"   Client ID: {client_id[:20]}...")
        except Exception as e:
            print(f"❌ Ошибка чтения credentials: {e}")
    else:
        print(f"❌ Файл credentials не найден: {creds_file}")
        return
    
    # Проверяем токен
    token_file = 'credentials/token.json'
    if os.path.exists(token_file):
        print("✅ Токен найден - OAuth2 настроен!")
        
        # Проверяем test_sheets.py
        test_file = 'test_sheets.py'
        if os.path.exists(test_file):
            print("✅ Тестовый скрипт готов")
            print()
            print("🚀 ГОТОВО К ТЕСТИРОВАНИЮ:")
            print("   python test_sheets.py")
        else:
            print("❌ Тестовый скрипт не найден")
            
    else:
        print("⏳ Токен не найден - необходима авторизация")
        print()
        print("📋 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. 🌐 Откройте OAuth URL в браузере")
        print("2. 👤 Войдите как: aleynikov.artem@gmail.com") 
        print("3. ✅ Разрешите доступ к Google Sheets")
        print("4. 📋 Скопируйте authorization code")
        print("5. 💾 Запустите: python save_token.py [КОД]")
        
        print()
        print("🔗 OAuth URL:")
        oauth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri=https%3A//developers.google.com/oauthplayground&"
            f"scope=https%3A//www.googleapis.com/auth/spreadsheets&"
            f"response_type=code&"
            f"access_type=offline"
        )
        print(oauth_url)
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    check_oauth_status()