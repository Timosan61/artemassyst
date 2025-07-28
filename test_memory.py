#!/usr/bin/env python3
"""
🧠 Тест памяти бота
Проверяет работу Zep Memory и контекста диалога
"""

import requests
import json
import time

BOT_URL = "https://artemassyst-bot-tt5dt.ondigitalocean.app"

def test_bot_status():
    """Проверить статус бота"""
    print("🔍 ПРОВЕРКА СТАТУСА БОТА:")
    try:
        response = requests.get(f"{BOT_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Статус: {data.get('status')}")
            print(f"🤖 AI: {data.get('ai_status')}")
            
            debug_info = data.get('debug_info', {})
            print(f"📊 Zep клиент: {debug_info.get('zep_client')}")
            print(f"🔗 OpenAI: {'✅' if debug_info.get('openai_enabled') else '❌'}")
            print(f"🔗 Anthropic: {'✅' if debug_info.get('anthropic_enabled') else '❌'}")
            print(f"📈 Сессий: {debug_info.get('user_sessions_count', 0)}")
            
            # Проверяем последнее обновление
            last_update = debug_info.get('last_update_time')
            if last_update:
                print(f"⏰ Последнее обновление: {last_update}")
            
            return True
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def test_memory_endpoint():
    """Тест эндпоинта проверки памяти"""
    print("\n🧠 ТЕСТ ПАМЯТИ:")
    test_session = "user_123456789"  # тестовая сессия
    
    try:
        response = requests.get(f"{BOT_URL}/debug/memory/{test_session}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Эндпоинт памяти работает")
            print(f"📊 Сообщений в сессии: {data.get('message_count', 0)}")
            return True
        else:
            print(f"❌ Эндпоинт памяти недоступен: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка теста памяти: {e}")
        return False

def check_version_update():
    """Проверить обновилась ли версия"""
    print("\n🔄 ПРОВЕРКА ВЕРСИИ:")
    try:
        response = requests.get(f"{BOT_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            version_info = data.get('debug_info', {}).get('version_info', {})
            last_commit = version_info.get('last_commit_sha', '')
            
            # Последний коммит должен начинаться с 5a3dcb7c
            if last_commit.startswith('5a3dcb7c'):
                print(f"✅ Версия обновлена: {last_commit}")
                print("🎉 Новый код с роутером LLM активен!")
                return True
            else:
                print(f"⚠️ Старая версия: {last_commit}")
                print("🔄 Деплой еще не завершился")
                return False
        else:
            print("❌ Не удалось получить информацию о версии")
            return False
    except Exception as e:
        print(f"❌ Ошибка проверки версии: {e}")
        return False

def main():
    print("🧠 ТЕСТИРОВАНИЕ ПАМЯТИ ARTEMASSYST БОТА")
    print("="*50)
    
    # Проверяем статус
    bot_ok = test_bot_status()
    
    if not bot_ok:
        print("\n❌ Бот недоступен, тестирование невозможно")
        return
    
    # Проверяем версию
    version_ok = check_version_update()
    
    # Тестируем память
    memory_ok = test_memory_endpoint()
    
    print("\n" + "="*50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    
    if bot_ok:
        print("✅ Бот работает")
    else:
        print("❌ Бот недоступен")
    
    if version_ok:
        print("✅ Новая версия активна")
    else:
        print("⚠️ Старая версия (деплой не завершен)")
    
    if memory_ok:
        print("✅ Эндпоинт памяти работает")
    else:
        print("❌ Проблемы с памятью")
    
    if version_ok and memory_ok:
        print("\n🎯 ГОТОВ К ТЕСТИРОВАНИЮ ДИАЛОГА!")
        print("Можно отправлять сообщения боту и проверять память")
    else:
        print("\n⏳ ОЖИДАНИЕ ДЕПЛОЯ...")
        print("Нужно дождаться обновления или исправить автоматический деплой")
    
    print("="*50)

if __name__ == "__main__":
    main()