#!/usr/bin/env python3
"""
Тестовый скрипт с симуляцией authorization code
"""

import json

def generate_test_instructions():
    print("🎯 ФИНАЛЬНЫЙ СПОСОБ ПОЛУЧЕНИЯ AUTHORIZATION CODE")
    print("=" * 80)
    
    try:
        with open('credentials/client_secret.json', 'r') as f:
            config = json.load(f)
        client_id = config['installed']['client_id']
        client_secret = config['installed']['client_secret']
    except Exception as e:
        print(f"❌ Ошибка чтения credentials: {e}")
        return
    
    print(f"🆔 Client ID: {client_id}")
    print(f"🔐 Client Secret: {client_secret}")
    print()
    
    print("📋 ТОЧНЫЕ ШАГИ - СЛЕДУЙТЕ СТРОГО:")
    print("=" * 80)
    
    oauth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri=https%3A//developers.google.com/oauthplayground&"
        f"scope=https%3A//www.googleapis.com/auth/spreadsheets&"
        f"response_type=code&"
        f"access_type=offline"
    )
    
    print("1. 🌐 Откройте эту ссылку в браузере:")
    print()
    print(oauth_url)
    print()
    
    print("2. 👤 Войдите в Google как: aleynikov.artem@gmail.com")
    print()
    
    print("3. ✅ Нажмите 'Разрешить' для доступа к Google Sheets")
    print()
    
    print("4. 📋 Вас перенаправит на OAuth Playground")
    print("   В Step 2 будет 'Authorization code'")
    print()
    
    print("5. 💾 Скопируйте код и запустите:")
    print("   python save_token.py [ВАШ_КОД]")
    print()
    
    print("🔥 КРИТИЧЕСКИ ВАЖНО:")
    print("- Код действует только 10 минут!")
    print("- Сразу запускайте save_token.py после получения")
    print("- Используйте именно аккаунт aleynikov.artem@gmail.com")
    
    return oauth_url

if __name__ == "__main__":
    url = generate_test_instructions()
    
    print("\n" + "=" * 80)
    print("🚀 ГОТОВО К ИСПОЛЬЗОВАНИЮ!")
    print("Откройте ссылку выше в браузере и следуйте инструкциям")
    print("=" * 80)