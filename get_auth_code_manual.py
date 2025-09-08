#!/usr/bin/env python3
"""
Получение authorization code через OAuth Playground - ручной процесс
"""

import json
import urllib.parse

CREDENTIALS_FILE = 'credentials/client_secret.json'

def generate_oauth_playground_url():
    print("🎯 ПОЛУЧЕНИЕ AUTHORIZATION CODE ЧЕРЕЗ OAuth PLAYGROUND")
    print("=" * 80)
    
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
    
    # Создаем OAuth URL для Playground
    params = {
        'client_id': client_id,
        'redirect_uri': 'https://developers.google.com/oauthplayground',
        'scope': 'https://www.googleapis.com/auth/spreadsheets',
        'response_type': 'code',
        'access_type': 'offline',
        'include_granted_scopes': 'true'
    }
    
    oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    
    print("📋 ПОШАГОВЫЕ ДЕЙСТВИЯ:")
    print("=" * 80)
    print("1. 🌐 Откройте OAuth Playground:")
    print("   https://developers.google.com/oauthplayground")
    print()
    print("2. ⚙️ Нажмите на шестеренку (Settings) в правом верхнем углу")
    print()
    print("3. ✅ Отметьте 'Use your own OAuth credentials'")
    print()
    print("4. 📝 Введите:")
    print(f"   OAuth Client ID: {client_id}")
    print(f"   OAuth Client secret: {client_secret}")
    print()
    print("5. 🔒 Нажмите 'Close'")
    print()
    print("6. 🔍 Найдите 'Google Sheets API v4' в списке слева")
    print()
    print("7. ✅ Отметьте scope:")
    print("   https://www.googleapis.com/auth/spreadsheets")
    print()
    print("8. 🚀 Нажмите 'Authorize APIs'")
    print()
    print("9. 👤 Войдите как: aleynikov.artem@gmail.com")
    print()
    print("10. 📋 После авторизации СКОПИРУЙТЕ 'Authorization code' из Step 2")
    print()
    print("11. 💾 Запустите: python save_token.py [ВСТАВЬТЕ_КОД_СЮДА]")
    print()
    
    print("🔗 ПРЯМАЯ ССЫЛКА для авторизации:")
    print("=" * 80)
    print(oauth_url)
    print("=" * 80)
    print()
    
    print("⚠️ ВАЖНО:")
    print("- Используйте аккаунт: aleynikov.artem@gmail.com")
    print("- Код авторизации появится в Step 2 OAuth Playground")
    print("- Код действует 10 минут - используйте быстро!")
    print()
    
    print("🎉 ПОСЛЕ ПОЛУЧЕНИЯ КОДА:")
    print("python save_token.py [YOUR_AUTHORIZATION_CODE]")

if __name__ == "__main__":
    generate_oauth_playground_url()