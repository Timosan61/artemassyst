#!/usr/bin/env python3
"""
Тестирование redirect_uri для n8n и других автоматизаций
"""

import json
import urllib.parse

CREDENTIALS_FILE = 'credentials/client_secret.json'

# Варианты redirect_uri используемые в n8n и других сервисах
N8N_REDIRECT_URIS = [
    # n8n стандартные
    "https://app.n8n.io/oauth2/callback",
    "http://localhost:5678/oauth2-credential/callback",
    "http://localhost:5678/rest/oauth2-credential/callback",
    
    # Zapier
    "https://zapier.com/dashboard/auth/oauth/return/",
    
    # Make (Integromat)
    "https://www.integromat.com/oauth/cb/google",
    
    # Общие для автоматизаций
    "https://oauth.pstmn.io/v1/callback",  # Postman
    "https://oauth-redirect.googleusercontent.com/",
    "https://developers.google.com/oauthplayground",
    
    # Возможные кастомные для вашего проекта
    "https://n8n.aleynikov.artem/oauth2/callback",
    "https://bot.aleynikov.artem/oauth/callback",
]

def create_oauth_urls():
    # Читаем credentials
    with open(CREDENTIALS_FILE, 'r') as f:
        config = json.load(f)
    
    client_id = config['installed']['client_id']
    scope = "https://www.googleapis.com/auth/spreadsheets"
    
    print("🔍 Тестирование redirect_uri для n8n и автоматизаций")
    print("=" * 80)
    print()
    print("📌 Так как API работает в n8n, один из этих URI должен быть настроен:")
    print()
    
    for i, redirect_uri in enumerate(N8N_REDIRECT_URIS, 1):
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
        
        print(f"📍 Вариант {i}: {redirect_uri}")
        print(f"   URL: {oauth_url}")
        print()
    
    print("=" * 80)
    print()
    print("🔧 Альтернативное решение - использовать Google OAuth Playground:")
    print("1. Откройте https://developers.google.com/oauthplayground")
    print("2. В настройках (шестеренка) выберите 'Use your own OAuth credentials'")
    print("3. Введите ваш Client ID и Client Secret")
    print("4. В Step 1 выберите 'Google Sheets API v4'")
    print("5. Авторизуйтесь и получите refresh token")
    print()
    print("📋 Если используете n8n:")
    print("1. В n8n credentials настройка должна показывать redirect URI")
    print("2. Этот URI нужно добавить в Google Cloud Console")
    print("3. Или проверьте какой URI уже настроен для работающего n8n")

if __name__ == "__main__":
    create_oauth_urls()