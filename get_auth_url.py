#!/usr/bin/env python3
"""
Генерация OAuth2 URL для авторизации Google Sheets
"""

import json
import urllib.parse
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials/client_secret.json'

def get_auth_url():
    print("🔍 Проверяю файл учетных данных...")
    
    # Проверяем файл учетных данных
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            creds_data = json.load(f)
        
        client_id = creds_data['installed']['client_id']
        print(f"✅ Client ID: {client_id}")
        
        if 'YOUR_GOOGLE_CLIENT_ID_HERE' in client_id:
            print("❌ Файл содержит шаблонные значения!")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")
        return None
    
    try:
        print("🔑 Создаю OAuth2 flow...")
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        flow.redirect_uri = 'http://localhost'
        
        print("🔗 Генерирую authorization URL...")
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        print("\n" + "=" * 80)
        print("🔗 OAuth2 Authorization URL:")
        print("=" * 80)
        print(f"{auth_url}")
        print("=" * 80)
        print()
        
        # Парсим URL для проверки
        parsed = urllib.parse.urlparse(auth_url)
        params = urllib.parse.parse_qs(parsed.query)
        
        print("🔍 Параметры URL:")
        print(f"   client_id: {params.get('client_id', ['MISSING'])[0]}")
        print(f"   scope: {params.get('scope', ['MISSING'])[0]}")
        print(f"   redirect_uri: {params.get('redirect_uri', ['MISSING'])[0]}")
        print(f"   response_type: {params.get('response_type', ['MISSING'])[0]}")
        print()
        
        print("📋 Инструкции:")
        print("1. Скопируйте URL выше")
        print("2. Откройте в браузере")
        print("3. Войдите как: aleynikov.artem@gmail.com")
        print("4. Разрешите доступ к Google Sheets")
        print("5. Скопируйте authorization code из адресной строки")
        print("   (после 'code=' и до '&' или конца URL)")
        print("6. Запустите: python save_token.py [КОД]")
        print()
        print("🔧 Альтернативный способ:")
        print("   Если URL не работает, можно создать вручную на:")
        print("   https://console.cloud.google.com/apis/credentials")
        
        return auth_url
        
    except Exception as e:
        print(f"❌ Ошибка создания URL: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    get_auth_url()