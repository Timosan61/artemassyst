#!/usr/bin/env python3
"""
Прямой тест OAuth2 - альтернативный метод получения токена
"""

import json
import urllib.parse
import webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials/client_secret.json'
TOKEN_FILE = 'credentials/token.json'

def direct_oauth_flow():
    print("🚀 ПРЯМОЙ OAuth2 ПОТОК - АЛЬТЕРНАТИВНЫЙ МЕТОД")
    print("=" * 80)
    
    try:
        # Создаем flow с локальным сервером
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, 
            SCOPES,
            redirect_uri='http://localhost:8080'
        )
        
        print("📋 АВТОМАТИЧЕСКИЙ ЗАПУСК АВТОРИЗАЦИИ")
        print("-" * 60)
        print("1. 🌐 Браузер откроется автоматически")
        print("2. 👤 Войдите как: aleynikov.artem@gmail.com")  
        print("3. ✅ Разрешите доступ к Google Sheets")
        print("4. 🔄 Код обработается автоматически")
        print()
        
        # Запускаем локальный сервер и получаем токен
        print("⏳ Запускаем локальный OAuth сервер...")
        
        # Попробуем разные порты если 8080 не работает
        ports_to_try = [8080, 8081, 8082, 9000, 9001]
        
        for port in ports_to_try:
            try:
                print(f"🔄 Пробуем порт {port}...")
                
                # Обновляем redirect_uri для текущего порта
                flow.redirect_uri = f'http://localhost:{port}'
                
                # Запускаем локальный сервер
                creds = flow.run_local_server(port=port, open_browser=True)
                
                # Сохраняем токен
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
                
                print(f"✅ Токен успешно получен через порт {port}!")
                print(f"💾 Токен сохранен в {TOKEN_FILE}")
                
                return True
                
            except Exception as e:
                print(f"❌ Порт {port} не сработал: {e}")
                continue
        
        print("❌ Все порты не сработали")
        return False
        
    except Exception as e:
        print(f"❌ Ошибка OAuth flow: {e}")
        return False

def generate_manual_url():
    print("\n🔗 РЕЗЕРВНЫЙ МЕТОД - РУЧНАЯ АВТОРИЗАЦИЯ")
    print("=" * 80)
    
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            config = json.load(f)
        client_id = config['installed']['client_id']
    except Exception as e:
        print(f"❌ Ошибка чтения credentials: {e}")
        return
    
    # Создаем URL для ручной авторизации
    params = {
        'client_id': client_id,
        'redirect_uri': 'https://developers.google.com/oauthplayground',
        'scope': 'https://www.googleapis.com/auth/spreadsheets',
        'response_type': 'code',
        'access_type': 'offline',
        'include_granted_scopes': 'true'
    }
    
    oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    
    print("📋 Если автоматический метод не работает:")
    print("1. 🌐 Откройте эту ссылку в обычном браузере:")
    print()
    print(oauth_url)
    print()
    print("2. 👤 Войдите как: aleynikov.artem@gmail.com")
    print("3. ✅ Разрешите доступ к Google Sheets")
    print("4. 📋 Скопируйте authorization code из OAuth Playground")
    print("5. 💾 Запустите: python save_token.py [КОД]")

if __name__ == "__main__":
    print("🎯 ТЕСТИРОВАНИЕ OAUTH2 - МНОЖЕСТВЕННЫЕ МЕТОДЫ")
    print("=" * 80)
    
    # Сначала пробуем автоматический метод
    success = direct_oauth_flow()
    
    if not success:
        # Если не получилось, показываем ручной метод
        generate_manual_url()
        
    else:
        print("\n🎉 ИНТЕГРАЦИЯ ГОТОВА!")
        print("=" * 80)
        print("✅ OAuth2 авторизация завершена")
        print("✅ Токен сохранен")
        print()
        print("📋 Следующие шаги:")
        print("1. Запустите: python test_sheets.py")
        print("2. Проверьте интеграцию с ботом")