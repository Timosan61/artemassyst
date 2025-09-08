#!/usr/bin/env python3
"""
Использование OAuth Playground для получения authorization code
"""

import json

CREDENTIALS_FILE = 'credentials/client_secret.json'

def show_oauth_playground_steps():
    print("🎯 ИСПОЛЬЗУЕМ OAuth PLAYGROUND")
    print("=" * 80)
    
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            config = json.load(f)
        client_id = config['installed']['client_id']
        client_secret = config['installed']['client_secret']
    except Exception as e:
        print(f"❌ Ошибка чтения credentials: {e}")
        return
    
    print("✅ OAuth Playground URI добавлен в консоли!")
    print("✅ Локальный сервер можно добавить позже")
    print()
    
    print("📋 ПОШАГОВЫЕ ДЕЙСТВИЯ:")
    print("=" * 80)
    print("1. 🌐 Откройте: https://developers.google.com/oauthplayground")
    print()
    print("2. ⚙️ Нажмите на шестеренку (Settings) в правом верхнем углу")
    print()
    print("3. ✅ Отметьте галочку 'Use your own OAuth credentials'")
    print()
    print("4. 📝 Заполните поля:")
    print(f"   OAuth Client ID: {client_id}")
    print(f"   OAuth Client secret: {client_secret}")
    print()
    print("5. 🔒 Нажмите 'Close' для сохранения настроек")
    print()
    print("6. 🔍 В левом списке найдите и раскройте 'Google Sheets API v4'")
    print()
    print("7. ✅ Отметьте галочку:")
    print("   https://www.googleapis.com/auth/spreadsheets")
    print()
    print("8. 🚀 Нажмите большую синюю кнопку 'Authorize APIs'")
    print()
    print("9. 👤 Войдите как: aleynikov.artem@gmail.com")
    print("   Разрешите доступ к Google Sheets")
    print()
    print("10. 📋 Скопируйте полученный 'Authorization code'")
    print()
    print("11. 💾 Запустите:")
    print("    python save_token.py [ВСТАВЬТЕ_КОД_СЮДА]")
    print()
    
    print("🎯 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:")
    print("=" * 80)
    print("После ввода authorization code:")
    print("✅ Токен сохранится в credentials/token.json")
    print("✅ Автоматически создастся Google таблица 'Алена - CRM'")
    print("✅ Интеграция бота с Google Sheets будет готова")
    print()
    
    print("❓ ЕСЛИ ВОЗНИКНУТ ПРОБЛЕМЫ:")
    print("1. Убедитесь что OAuth Playground URI добавлен в консоли")
    print("2. Подождите 2-3 минуты после добавления URI")
    print("3. Попробуйте в режиме инкогнито")
    print("4. Используйте аккаунт aleynikov.artem@gmail.com")
    print()
    
    print("🔥 ДЕЙСТВУЙТЕ СЕЙЧАС - ФИНАЛЬНЫЙ ШАГ!")

if __name__ == "__main__":
    show_oauth_playground_steps()