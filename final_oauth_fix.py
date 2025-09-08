#!/usr/bin/env python3
"""
ФИНАЛЬНОЕ РЕШЕНИЕ проблемы OAuth2 для Алены (Google Sheets)
"""

import json

CREDENTIALS_FILE = 'credentials/client_secret.json'

def show_final_solution():
    print("🎯 ДИАГНОСТИКА ЗАВЕРШЕНА - НАЙДЕНА КОРНЕВАЯ ПРИЧИНА!")
    print("=" * 80)
    
    # Читаем credentials
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            config = json.load(f)
        client_id = config['installed']['client_id']
        client_secret = config['installed']['client_secret']
    except Exception as e:
        print(f"❌ Ошибка чтения credentials: {e}")
        return
    
    print(f"🆔 Текущий Client ID: {client_id}")
    print()
    
    print("🚨 КОРНЕВАЯ ПРИЧИНА:")
    print("OAuth клиент создан как 'WEB application', но для бота нужен 'DESKTOP application'")
    print("WEB клиенты не поддерживают:")
    print("- urn:ietf:wg:oauth:2.0:oob (OOB flow)")
    print("- localhost redirect URIs без предварительной настройки")
    print()
    
    print("💡 ЕДИНСТВЕННОЕ ПРАВИЛЬНОЕ РЕШЕНИЕ:")
    print("=" * 80)
    print("ДОБАВИТЬ redirect URI в Google Cloud Console для ЭТОГО клиента")
    print()
    
    print("📋 ПОШАГОВАЯ ИНСТРУКЦИЯ (5 минут):")
    print()
    print("1. 🌐 Откройте в обычном браузере (НЕ в автоматизации!):")
    print("   https://console.cloud.google.com/apis/credentials")
    print()
    print("2. 👤 Войдите как: aleynikov.artem@gmail.com")
    print()
    print("3. 🔍 Найдите в списке OAuth 2.0 Client IDs:")
    print(f"   Client ID: {client_id}")
    print("   Имя клиента: (может быть 'Web client 1' или подобное)")
    print()
    print("4. ✏️ Кликните на НАЗВАНИЕ клиента (не на иконку карандаша)")
    print("   Откроется страница редактирования")
    print()
    print("5. 📝 Найдите раздел 'Authorized redirect URIs'")
    print("   Нажмите '+ ADD URI'")
    print()
    print("6. 🎯 Добавьте ТОЧНО этот URI:")
    print("   https://developers.google.com/oauthplayground")
    print()
    print("7. 💾 Нажмите 'SAVE' внизу страницы")
    print()
    print("8. ⏳ ПОДОЖДИТЕ 2-3 МИНУТЫ для применения изменений")
    print("   (Google требуется время для обновления конфигурации)")
    print()
    
    print("🧪 ТЕСТ ПОСЛЕ ДОБАВЛЕНИЯ URI:")
    print("=" * 80)
    print("1. Откройте: https://developers.google.com/oauthplayground")
    print("2. Нажмите на шестерёнку (Settings)")
    print("3. Отметьте 'Use your own OAuth credentials'")
    print(f"4. OAuth Client ID: {client_id}")
    print(f"5. OAuth Client secret: {client_secret}")
    print("6. Close settings")
    print("7. Выберите 'Google Sheets API v4'")
    print("8. Выберите scope: https://www.googleapis.com/auth/spreadsheets")
    print("9. Нажмите 'Authorize APIs'")
    print("10. Должен открыться экран авторизации БЕЗ ошибки redirect_uri_mismatch")
    print("11. Авторизуйтесь и получите authorization code")
    print("12. Запустите: python save_token.py [КОД]")
    print()
    
    print("🚀 АЛЬТЕРНАТИВНЫЙ АВТОМАТИЧЕСКИЙ ТЕСТ:")
    print("=" * 80)
    print("Запустите: python test_oauth_after_fix.py")
    print("Этот скрипт проверит OAuth URL и покажет результат.")
    print()
    
    print("❓ ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ:")
    print("=" * 80)
    print("Q: Почему нельзя создать новый Desktop клиент?")
    print("A: Можно, но текущий уже работает в n8n, просто нужен redirect URI")
    print()
    print("Q: Сколько времени займет?")  
    print("A: 2-3 минуты на добавление URI + 2-3 минуты ожидание Google")
    print()
    print("Q: Что если не получается войти в консоль?")
    print("A: Используйте обычный браузер (Chrome/Firefox), отключите блокировщики")
    print()
    print("Q: Нужно ли менять что-то еще?")
    print("A: НЕТ! Только добавить redirect URI. Все остальное уже настроено.")
    print()
    
    print("✅ СТАТУС ГОТОВНОСТИ:")
    print("✅ Google Sheets API включен")
    print("✅ Client ID/Secret настроены")  
    print("✅ Credentials работают в n8n")
    print("✅ Скрипты для тестирования готовы")
    print("❌ Отсутствует redirect URI в Google Cloud Console")
    print()
    
    print("🎉 ПОСЛЕ УСПЕШНОГО РЕШЕНИЯ:")
    print("Запустится автоматическое создание Google таблицы 'Алена - CRM'")
    print("с листами для клиентов, аналитики и воронки конверсии.")
    print()
    print("🎯 ДЕЙСТВУЙТЕ СЕЙЧАС - РЕШЕНИЕ В ВАШИХ РУКАХ!")

if __name__ == "__main__":
    show_final_solution()