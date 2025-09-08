#!/usr/bin/env python3
"""
Упрощенный тест конфигурации Google Sheets
"""

import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sheets_config():
    """Тест конфигурации листов"""
    print("🔧 Тест конфигурации Google Sheets интеграции")
    print("=" * 50)
    
    try:
        from bot.integrations.sheets_config import SHEET_CONFIGURATIONS, TARGET_EMAIL
        
        print(f"📧 Целевой email: {TARGET_EMAIL}")
        print(f"📊 Настроено {len(SHEET_CONFIGURATIONS)} листов:\n")
        
        for sheet_key, config in SHEET_CONFIGURATIONS.items():
            print(f"📋 Лист '{config['name']}':")
            print(f"   🔹 ID: {sheet_key}")
            print(f"   🔹 Колонок: {len(config['headers'])}")
            
            if sheet_key == 'clients':
                print("   🔹 Основные поля клиентов:")
                for i, header in enumerate(config['headers'][:10]):
                    print(f"      {i+1:2d}. {header}")
                if len(config['headers']) > 10:
                    print(f"      ... и еще {len(config['headers']) - 10} полей")
            print()
        
        print("✅ Конфигурация корректна!")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_credentials():
    """Тест наличия файлов учетных данных"""
    print("\n🔐 Тест файлов учетных данных")
    print("=" * 50)
    
    credentials_file = "credentials/client_secret.json"
    example_file = "credentials/client_secret.json.example"
    
    if os.path.exists(credentials_file):
        print(f"✅ Найден {credentials_file}")
        
        try:
            import json
            with open(credentials_file, 'r') as f:
                creds = json.load(f)
            
            client_id = creds.get('installed', {}).get('client_id', '')
            client_secret = creds.get('installed', {}).get('client_secret', '')
            
            if 'YOUR_GOOGLE_CLIENT_ID_HERE' in client_id:
                print("⚠️  Файл содержит шаблонные значения")
                print("   Обновите client_id и client_secret реальными данными")
            else:
                print("✅ Файл содержит реальные учетные данные")
                print(f"   Client ID: {client_id[:20]}...")
                
        except Exception as e:
            print(f"❌ Ошибка чтения файла: {e}")
            
    else:
        print(f"❌ Не найден {credentials_file}")
        
        if os.path.exists(example_file):
            print(f"💡 Найден {example_file}")
            print(f"   Скопируйте его: cp {example_file} {credentials_file}")
        else:
            print(f"❌ Не найден {example_file}")

def test_dependencies():
    """Тест наличия зависимостей Google API"""
    print("\n📦 Тест зависимостей Google API")
    print("=" * 50)
    
    required_modules = [
        'google.auth',
        'google.auth.transport.requests', 
        'google_auth_oauthlib.flow',
        'googleapiclient.discovery',
        'googleapiclient.errors'
    ]
    
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            missing.append(module)
    
    if missing:
        print(f"\n⚠️  Отсутствуют зависимости: {len(missing)}")
        print("Установите их:")
        print("pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        return False
    else:
        print("\n✅ Все зависимости установлены!")
        return True

if __name__ == "__main__":
    print("🚀 Google Sheets Integration Configuration Test")
    
    # Тесты
    config_ok = test_sheets_config()
    test_credentials()
    deps_ok = test_dependencies()
    
    print("\n" + "=" * 50)
    print("📋 Результаты:")
    print(f"   Конфигурация: {'✅' if config_ok else '❌'}")
    print(f"   Зависимости: {'✅' if deps_ok else '❌'}")
    
    if config_ok and deps_ok:
        print("\n🎯 Конфигурация готова!")
        print("📝 Следующие шаги:")
        print("1. Убедитесь что credentials/client_secret.json содержит реальные данные")
        print("2. Установите GOOGLE_SHEETS_ENABLED=true в .env")
        print("3. Запустите полный тест: python test_google_sheets.py")
    else:
        print("\n⚠️  Требуется настройка. См. инструкции выше.")