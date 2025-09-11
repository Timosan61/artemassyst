#!/usr/bin/env python3
"""
Чистый тест системы памяти с новой сессией
"""
import asyncio
import os
import uuid
from dotenv import load_dotenv
from bot.memory.memory_service import MemoryService

# Загружаем переменные окружения
load_dotenv()

async def test_clean_conversation():
    """Тестирует новую сессию без конфликтов с данными"""
    
    # Получаем ZEP API ключ
    zep_api_key = os.getenv('ZEP_API_KEY')
    if not zep_api_key:
        print("❌ ZEP_API_KEY не найден")
        return
    
    print(f"🔑 Используем ZEP API Key: {zep_api_key[:8]}...{zep_api_key[-4:]}")
    
    # Инициализируем сервис памяти
    memory_service = MemoryService(zep_api_key, enable_memory=True)
    print("✅ MemoryService инициализирован")
    
    # Новая уникальная сессия
    test_session_id = f"test_clean_{uuid.uuid4().hex[:8]}"
    print(f"🆔 Используем сессию: {test_session_id}")
    
    # Симулируем диалог пошагово
    messages = [
        ("привет", "user"),
        ("Здравствуйте! Ищете недвижимость для себя или как инвестицию?", "assistant"),
        ("из Волгодонска прилечу завтра", "user"),
        ("Отлично! Волгодонск хороший город. Какая цель покупки?", "assistant"),
        ("длинные инвестиции", "user"),
        ("Понятно, длинные инвестиции. Какую недвижимость рассматриваете?", "assistant"),
        ("дом в красной поляне до 5 млн", "user"),
    ]
    
    print(f"\n📝 Тестируем пошаговую обработку...")
    
    for i, (message, msg_type) in enumerate(messages):
        print(f"\n--- Шаг {i+1}: {msg_type} ---")
        print(f"📨 '{message}'")
        
        try:
            result = await memory_service.process_message(
                user_id=test_session_id,
                message_text=message,
                message_type=msg_type
            )
            
            if result.get('success'):
                lead_data = result.get('lead_data')
                current_state = result.get('current_state')
                
                print(f"✅ Успешно обработано")
                print(f"   📊 Состояние: {current_state}")
                
                if lead_data:
                    data_parts = []
                    if lead_data.name:
                        data_parts.append(f"Имя: {lead_data.name}")
                    if getattr(lead_data, 'city', None):
                        data_parts.append(f"Город: {lead_data.city}")
                    if lead_data.automation_goal:
                        data_parts.append(f"Цель: {lead_data.automation_goal.value}")
                    if lead_data.budget_max:
                        data_parts.append(f"Бюджет: до {lead_data.budget_max}")
                    if getattr(lead_data, 'preferred_locations', None):
                        data_parts.append(f"Локации: {lead_data.preferred_locations}")
                    if getattr(lead_data, 'property_type', None):
                        data_parts.append(f"Тип: {lead_data.property_type}")
                    if getattr(lead_data, 'urgency_date', None):
                        data_parts.append(f"Приезд: {lead_data.urgency_date}")
                    
                    if data_parts:
                        print(f"   📋 Данные: {' | '.join(data_parts)}")
                    else:
                        print(f"   📋 Данные пока не извлечены")
                        
            else:
                print(f"❌ Ошибка: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Исключение: {e}")
    
    print(f"\n🏁 === ФИНАЛЬНАЯ ПРОВЕРКА ===")
    
    try:
        # Получаем финальные данные
        final_lead = await memory_service.get_lead_data(test_session_id)
        
        print(f"\n📋 Итоговые данные лида:")
        if final_lead.name:
            print(f"   - Имя: {final_lead.name}")
        if getattr(final_lead, 'city', None):
            print(f"   - Город: {final_lead.city}")
        if final_lead.automation_goal:
            print(f"   - Цель: {final_lead.automation_goal.value}")
        if final_lead.budget_max:
            print(f"   - Бюджет: до {final_lead.budget_max} руб")
        if getattr(final_lead, 'preferred_locations', None):
            print(f"   - Локации: {final_lead.preferred_locations}")
        if getattr(final_lead, 'property_type', None):
            print(f"   - Тип недвижимости: {final_lead.property_type}")
        if getattr(final_lead, 'urgency_date', None):
            print(f"   - Дата приезда: {final_lead.urgency_date}")
        print(f"   - Состояние: {final_lead.current_dialog_state.value}")
        
        print(f"\n🎯 РЕЗУЛЬТАТ:")
        if final_lead.city and final_lead.automation_goal and final_lead.budget_max:
            print("✅ Основные данные извлечены успешно!")
        else:
            print("⚠️  Некоторые данные не были извлечены")
            
    except Exception as e:
        print(f"❌ Ошибка финальной проверки: {e}")

if __name__ == "__main__":
    asyncio.run(test_clean_conversation())