#!/usr/bin/env python3
"""
Скрипт для тестирования системы памяти Zep
"""
import asyncio
import os
from dotenv import load_dotenv
from bot.memory.memory_service import MemoryService

# Загружаем переменные окружения
load_dotenv()

async def test_memory_system():
    """Тестирует сохранение и извлечение сообщений из памяти"""
    
    # Получаем ZEP API ключ
    zep_api_key = os.getenv('ZEP_API_KEY')
    if not zep_api_key:
        print("❌ ZEP_API_KEY не найден в переменных окружения")
        return
    
    print(f"🔑 Используем ZEP API Key: {zep_api_key[:8]}...{zep_api_key[-4:]}")
    
    # Инициализируем сервис памяти
    try:
        memory_service = MemoryService(zep_api_key, enable_memory=True)
        print("✅ MemoryService инициализирован")
    except Exception as e:
        print(f"❌ Ошибка инициализации MemoryService: {e}")
        return
    
    # Тестовые данные
    test_session_id = "test_user_123456"
    
    print(f"\n🧪 Тестируем сессию: {test_session_id}")
    
    # 1. Тестируем сохранение сообщений пользователя
    test_messages = [
        ("привет", "user"),
        ("артем", "user"), 
        ("ищу недвижимость", "user"),
        ("сочи", "user"),
        ("ПМЖ", "user"),
        ("Сириус", "user"),
        ("дом", "user"),
        ("ипотека", "user")
    ]
    
    print("\n📝 Сохраняем тестовые сообщения...")
    for message, msg_type in test_messages:
        try:
            result = await memory_service.process_message(
                user_id=test_session_id,
                message_text=message,
                message_type=msg_type
            )
            
            if result.get('success'):
                print(f"✅ Сохранено: '{message}' ({msg_type})")
            else:
                print(f"❌ Ошибка сохранения: '{message}' - {result.get('error', 'неизвестная ошибка')}")
                
        except Exception as e:
            print(f"❌ Исключение при сохранении '{message}': {e}")
    
    # 2. Тестируем извлечение истории
    print(f"\n📖 Извлекаем историю диалога...")
    try:
        dialog_history = await memory_service.get_dialog_history(test_session_id, limit=10)
        
        if dialog_history:
            print(f"✅ Найдено {len(dialog_history)} сообщений:")
            for i, msg in enumerate(dialog_history, 1):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                speaker_name = msg.get('speaker_name', 'unknown')
                print(f"  {i}. {role} ({speaker_name}): {content}")
        else:
            print("❌ История диалога пуста")
            
    except Exception as e:
        print(f"❌ Ошибка извлечения истории: {e}")
    
    # 3. Тестируем получение данных лида
    print(f"\n👤 Проверяем данные лида...")
    try:
        lead_data = await memory_service.get_lead_data(test_session_id)
        
        if lead_data:
            print(f"✅ Данные лида найдены:")
            print(f"  - Имя: {lead_data.name}")
            print(f"  - Город: {lead_data.current_location}")
            print(f"  - Цель: {lead_data.automation_goal}")
            print(f"  - Локация: {getattr(lead_data, 'preferred_locations', 'не указана')}")
            print(f"  - Статус: {lead_data.qualification_status}")
            print(f"  - Состояние диалога: {lead_data.current_dialog_state}")
        else:
            print("❌ Данные лида не найдены")
            
    except Exception as e:
        print(f"❌ Ошибка получения данных лида: {e}")
    
    # 4. Тестируем прямое подключение к Zep
    print(f"\n🔗 Тестируем прямое подключение к Zep...")
    try:
        if memory_service.zep_client:
            memory = await memory_service.zep_client.memory.get(session_id=test_session_id)
            
            if memory and memory.messages:
                print(f"✅ Прямое подключение к Zep работает. Найдено {len(memory.messages)} сообщений:")
                for i, msg in enumerate(memory.messages[-5:], 1):  # Последние 5
                    print(f"  {i}. {msg.role_type} ({msg.role}): {msg.content[:50]}...")
            else:
                print("❌ Сообщения в Zep не найдены")
        else:
            print("❌ Zep клиент не инициализирован")
            
    except Exception as e:
        print(f"❌ Ошибка прямого подключения к Zep: {e}")

if __name__ == "__main__":
    asyncio.run(test_memory_system())