#!/usr/bin/env python3
"""
Все варианты решения проблемы OAuth2 redirect_uri_mismatch
"""

import json

CREDENTIALS_FILE = 'credentials/client_secret.json'

def show_all_solutions():
    print("🚨 ПРОБЛЕМА: redirect_uri_mismatch")
    print("=" * 80)
    
    # Читаем client_id
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
    
    print("💡 ВАРИАНТЫ РЕШЕНИЯ:")
    print()
    
    print("🥇 ВАРИАНТ 1: Google Cloud Console (РЕКОМЕНДУЕТСЯ)")
    print("=" * 60)
    print("1. Откройте: https://console.cloud.google.com/apis/credentials")
    print("2. Войдите как: aleynikov.artem@gmail.com")
    print(f"3. Найдите Client ID: {client_id}")
    print("4. Добавьте redirect URI: https://developers.google.com/oauthplayground")
    print("5. Сохраните изменения")
    print("6. Подождите 2 минуты")
    print("7. Используйте OAuth Playground для авторизации")
    print()
    
    print("🥈 ВАРИАНТ 2: Прямой OAuth URL (если API работает в n8n)")
    print("=" * 60)
    print("Если API уже работает в n8n, попробуйте этот URL:")
    print()
    
    # Генерируем простой OAuth URL
    import urllib.parse
    redirect_uri = "urn:ietf:wg:oauth:2.0:oob"  # OOB flow
    scope = "https://www.googleapis.com/auth/spreadsheets"
    
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'response_type': 'code',
        'access_type': 'offline'
    }
    
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    query_string = urllib.parse.urlencode(params)
    oauth_url = f"{base_url}?{query_string}"
    
    print("🔗 OAuth URL (OOB flow):")
    print(oauth_url)
    print()
    print("Этот URL должен показать код прямо на экране.")
    print()
    
    print("🥉 ВАРИАНТ 3: Создание нового OAuth клиента")
    print("=" * 60)
    print("1. Откройте: https://console.cloud.google.com/apis/credentials")
    print("2. Нажмите '+ CREATE CREDENTIALS' → 'OAuth client ID'")
    print("3. Выберите тип: 'Desktop application'")
    print("4. Имя: 'Alena Bot OAuth Client'")
    print("5. Скачайте JSON файл")
    print("6. Замените credentials/client_secret.json")
    print()
    
    print("🏆 ВАРИАНТ 4: Service Account (альтернатива)")
    print("=" * 60)
    print("1. Создайте Service Account в Google Cloud Console")
    print("2. Скачайте ключ JSON")
    print("3. Поделитесь Google таблицей с email Service Account")
    print("4. Используйте Service Account для прямого доступа")
    print()
    
    print("🔧 СТАТУС ТЕКУЩЕЙ НАСТРОЙКИ:")
    print("✅ Client ID настроен")
    print("✅ Client Secret настроен")
    print("✅ Google Sheets API включен (работает в n8n)")
    print("❌ Redirect URI не добавлен в Google Cloud Console")
    print()
    
    print("📞 ДЛЯ БЫСТРОГО РЕШЕНИЯ:")
    print("Выберите ВАРИАНТ 1 - добавьте redirect URI в консоли.")
    print("Это займет 2 минуты и решит проблему навсегда.")
    print()
    
    print("✅ ПОСЛЕ РЕШЕНИЯ ЗАПУСТИТЕ:")
    print("python test_oauth_after_fix.py")

if __name__ == "__main__":
    show_all_solutions()