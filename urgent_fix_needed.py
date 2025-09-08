#!/usr/bin/env python3
"""
СРОЧНО: Добавить redirect URI в Google Cloud Console
"""

import json

CREDENTIALS_FILE = 'credentials/client_secret.json'

def show_urgent_fix():
    print("🚨 ПОДТВЕРЖДЕНИЕ: redirect_uri_mismatch с localhost:8080")
    print("=" * 80)
    
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            config = json.load(f)
        client_id = config['installed']['client_id']
        client_secret = config['installed']['client_secret']
    except Exception as e:
        print(f"❌ Ошибка чтения credentials: {e}")
        return
    
    print("✅ ДИАГНОСТИКА ПОДТВЕРЖДЕНА:")
    print("- localhost:8080 заблокирован")  
    print("- OAuth Playground заблокирован")
    print("- OOB flow заблокирован для WEB клиента")
    print("- API работает в n8n (значит credentials правильные)")
    print()
    
    print("🎯 ЕДИНСТВЕННОЕ РЕШЕНИЕ:")
    print("ДОБАВИТЬ redirect URI в Google Cloud Console")
    print()
    
    print("📱 СРОЧНЫЕ ДЕЙСТВИЯ (прямо сейчас):")
    print("=" * 80)
    print("1. Откройте на ТЕЛЕФОНЕ или ПЛАНШЕТЕ (чтобы избежать блокировки автоматизации):")
    print("   https://console.cloud.google.com/apis/credentials")
    print()
    print("2. Войдите как: aleynikov.artem@gmail.com")
    print()
    print("3. Найдите в списке:")
    print(f"   Client ID: {client_id}")
    print()
    print("4. Кликните на название клиента")
    print()
    print("5. Найдите раздел 'Authorized redirect URIs'")
    print("   Нажмите '+ ADD URI'")
    print()
    print("6. Добавьте ОБА URI:")
    print("   • https://developers.google.com/oauthplayground")
    print("   • http://localhost:8080")
    print()
    print("7. Нажмите 'SAVE'")
    print()
    print("8. Подождите 2 минуты")
    print()
    
    print("🧪 ПРОВЕРКА ПОСЛЕ ДОБАВЛЕНИЯ:")
    print("=" * 80)
    print("Вариант 1 (OAuth Playground):")
    print("1. https://developers.google.com/oauthplayground")
    print("2. Settings (шестеренка)")
    print("3. Use your own OAuth credentials ✓")
    print(f"4. Client ID: {client_id}")
    print(f"5. Client Secret: {client_secret}")
    print("6. Google Sheets API v4")
    print("7. https://www.googleapis.com/auth/spreadsheets")
    print("8. Authorize APIs")
    print()
    
    print("Вариант 2 (локальный сервер):")
    print("python local_oauth_server.py")
    print()
    
    print("🎯 РЕЗУЛЬТАТ:")
    print("После добавления URI получите authorization code")
    print("Затем: python save_token.py [КОД]")
    print("И: python test_sheets.py")
    print()
    
    print("💡 ПОЧЕМУ ЭТО РАБОТАЕТ В N8N?")
    print("N8N использует свои собственные redirect URI,")
    print("которые уже зарегистрированы в их системе.")
    print("Для бота нужны собственные redirect URI.")
    print()
    
    print("🔥 ДЕЙСТВУЙТЕ СЕЙЧАС! 🔥")
    print("Проблема решается за 3 минуты добавления URI.")

if __name__ == "__main__":
    show_urgent_fix()