#!/usr/bin/env python3
"""
Сохранение OAuth2 токена из authorization code
"""

import sys
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/tables'
]
CREDENTIALS_FILE = 'credentials/client_secret.json'
TOKEN_FILE = 'credentials/token.json'

def save_token(auth_code):
    try:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        flow.redirect_uri = 'https://developers.google.com/oauthplayground'
        
        # Получаем токен
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        # Сохраняем
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        
        print(f"✅ Токен сохранен в {TOKEN_FILE}")
        print("🎉 OAuth2 авторизация завершена!")
        print()
        print("📋 Следующие шаги:")
        print("1. Запустите тест: python test_sheets.py")
        print("2. Или проверьте интеграцию с ботом")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python save_token.py [AUTHORIZATION_CODE]")
        sys.exit(1)
    
    auth_code = sys.argv[1]
    success = save_token(auth_code)
    sys.exit(0 if success else 1)