#!/usr/bin/env python3
"""
Инструкции для ручного добавления redirect URI в Google Cloud Console
"""

import json

CREDENTIALS_FILE = 'credentials/client_secret.json'

def show_manual_fix():
    print("🚨 КРИТИЧЕСКАЯ ОШИБКА: redirect_uri_mismatch")
    print("=" * 80)
    
    # Читаем client_id
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            config = json.load(f)
        client_id = config['installed']['client_id']
    except Exception as e:
        print(f"❌ Ошибка чтения credentials: {e}")
        return
    
    print(f"🆔 Ваш Client ID: {client_id}")
    print()
    
    print("📋 СРОЧНЫЕ ДЕЙСТВИЯ:")
    print()
    print("1. 🌐 Откройте в браузере (НЕ в автоматизации):")
    print("   https://console.cloud.google.com/apis/credentials")
    print()
    print("2. 👤 Войдите как: aleynikov.artem@gmail.com")
    print()
    print("3. 🔍 Найдите OAuth 2.0 Client ID:")
    print(f"   {client_id}")
    print("   (должен называться 'Desktop application')")
    print()
    print("4. ✏️ Кликните на имя клиента для редактирования")
    print()
    print("5. ➕ В разделе 'Authorized redirect URIs' нажмите 'ADD URI'")
    print()
    print("6. 📝 Добавьте следующий URI:")
    print("   https://developers.google.com/oauthplayground")
    print()
    print("7. 💾 Нажмите 'SAVE' внизу страницы")
    print()
    print("8. ⏳ Подождите 1-2 минуты для применения изменений")
    print()
    
    print("=" * 80)
    print()
    print("🔄 ПОСЛЕ ДОБАВЛЕНИЯ URI:")
    print("1. Вернитесь к OAuth Playground:")
    print("   https://developers.google.com/oauthplayground")
    print("2. Убедитесь что настройки сохранены (шестеренка)")
    print("3. Попробуйте 'Authorize APIs' снова")
    print()
    
    print("📞 ЕСЛИ НУЖНА ПОМОЩЬ:")
    print("- Client ID уже настроен правильно")
    print("- Client Secret уже настроен правильно") 
    print("- Нужно добавить ТОЛЬКО redirect URI")
    print("- API Google Sheets уже включен")
    print()
    
    print("✅ КОГДА ГОТОВО:")
    print("Запустите: python test_oauth_after_fix.py")

if __name__ == "__main__":
    show_manual_fix()