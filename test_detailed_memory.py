#!/usr/bin/env python3
"""
Детальный тест системы памяти - проверяем извлечение данных из конкретных сообщений
"""
import asyncio
import os
from dotenv import load_dotenv
from bot.memory.memory_service import MemoryService

# Загружаем переменные окружения
load_dotenv()

async def test_specific_conversation():
    """Тестирует конкретный диалог из Telegram"""
    
    # Получаем ZEP API ключ
    zep_api_key = os.getenv('ZEP_API_KEY')
    if not zep_api_key:
        print("❌ ZEP_API_KEY не найден")
        return
    
    print(f"🔑 Используем ZEP API Key: {zep_api_key[:8]}...{zep_api_key[-4:]}")
    
    # Инициализируем сервис памяти
    memory_service = MemoryService(zep_api_key, enable_memory=True)
    print("✅ MemoryService инициализирован")
    
    # Тестовая сессия
    import time
    test_session_id = f"test_fixed_conversation_{int(time.time())}"  # Уникальная сессия для каждого теста
    
    # Симулируем реальный диалог
    conversation = [
        ("привет, продолжим", "user"),
        ("Здравствуйте, Артем! Конечно, давайте продолжим...", "assistant"),
        ("красная поляна", "user"),
        ("Отличный выбор! Красная Поляна...", "assistant"),
        ("дом, до 5 млн рублей", "user"),
        ("Спасибо за уточнение! Дом до 5 миллионов...", "assistant"),
        ("из Волгодонск на супер джете прилечу", "user"),
        ("Отлично, спасибо за информацию...", "assistant"),
        ("завтра буду или после завтра , незнаю", "user"),
        ("Поняла, спасибо за уточнение...", "assistant"),
        ("как инвестицию", "user"),
        ("Отлично, инвестиции в недвижимость...", "assistant"),
        ("длинные", "user"),
        ("Спасибо за уточнение! Длинные инвестиции...", "assistant")
    ]
    
    print(f"\n📝 Обрабатываем диалог...")
    lead_data = None
    
    for i, (message, msg_type) in enumerate(conversation):
        print(f"\n--- Сообщение {i+1}: {msg_type} ---")
        print(f"📨 '{message[:50]}...'")
        
        try:
            result = await memory_service.process_message(
                user_id=test_session_id,
                message_text=message,
                message_type=msg_type
            )
            
            if result.get('success'):
                lead_data = result.get('lead_data')
                current_state = result.get('current_state')
                
                print(f"✅ Обработано успешно")
                print(f"   Состояние: {current_state}")
                
                # Показываем что извлекли
                if lead_data:
                    print(f"   📊 Текущие данные лида:")
                    if lead_data.name:
                        print(f"      - Имя: {lead_data.name}")
                    if hasattr(lead_data, 'city') and lead_data.city:
                        print(f"      - Город: {lead_data.city}")
                    if lead_data.automation_goal:
                        print(f"      - Цель: {lead_data.automation_goal}")
                    if lead_data.budget_max:
                        print(f"      - Бюджет до: {lead_data.budget_max}")
                    if hasattr(lead_data, 'preferred_locations'):
                        print(f"      - Локации: {lead_data.preferred_locations}")
            else:
                print(f"❌ Ошибка: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Исключение: {e}")
        
        # Добавляем задержку чтобы избежать 429 Too Many Requests
        await asyncio.sleep(0.5)
    
    # Проверяем финальное состояние
    print(f"\n🏁 === ФИНАЛЬНАЯ ПРОВЕРКА ===")
    
    try:
        # Получаем финальные данные лида
        final_lead = await memory_service.get_lead_data(test_session_id)
        
        print(f"\n📋 Финальные данные лида:")
        print(f"   - Имя: {final_lead.name}")
        print(f"   - Город: {getattr(final_lead, 'city', 'НЕ СОХРАНЕН')}")
        print(f"   - Цель: {final_lead.automation_goal}")
        print(f"   - Бюджет: {final_lead.budget_min}-{final_lead.budget_max}")
        print(f"   - Состояние диалога: {final_lead.current_dialog_state}")
        
        # Получаем историю
        history = await memory_service.get_dialog_history(test_session_id, limit=20)
        print(f"\n📜 История диалога: {len(history)} сообщений")
        
        # Проверяем, есть ли в истории информация о городе
        print(f"\n🔍 Поиск упоминаний города в истории:")
        for msg in history:
            if 'волгодонск' in msg.get('content', '').lower():
                print(f"   ✅ Найдено: {msg.get('content')[:100]}...")
            if 'сочи' in msg.get('content', '').lower():
                print(f"   ✅ Найдено про Сочи: {msg.get('content')[:100]}...")
                
    except Exception as e:
        print(f"❌ Ошибка финальной проверки: {e}")
    
    print("\n" + "="*50)
    print("🎯 ВЫВОД: Проблема в том, что город НЕ извлекается из сообщений!")
    print("         Нужно добавить логику извлечения города в LeadDataExtractor")

if __name__ == "__main__":
    asyncio.run(test_specific_conversation())