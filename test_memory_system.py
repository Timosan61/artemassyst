#!/usr/bin/env python3
"""
Тестирование интеллектуальной системы памяти "Алёна"
"""
import asyncio
import json
from bot.memory import MemoryService, DialogState, ClientType

async def test_memory_system():
    """Тестирует систему памяти в действии"""
    print("🧠 Тест интеллектуальной системы памяти 'Алёна'\n")
    
    # Инициализируем сервис (в тестовом режиме без ZEP)
    memory_service = MemoryService("test_key", enable_memory=False)
    
    # Тестовый сценарий диалога
    session_id = "test_user_123"
    
    test_messages = [
        "Привет! Интересует автоматизация для бизнеса",
        "У меня интернет-магазин одежды в Москве", 
        "Хочу автоматизировать общение с клиентами и увеличить продажи",
        "Готов потратить до $1000 на хорошее решение",
        "Нужна интеграция с моей CRM системой",
        "Когда можем посмотреть демо? Готов завтра"
    ]
    
    print("📝 Симуляция диалога:\n")
    
    for i, message in enumerate(test_messages, 1):
        print(f"👤 Сообщение {i}: {message}")
        
        # Обрабатываем сообщение через систему памяти
        result = await memory_service.process_message(session_id, message)
        
        if result['success']:
            lead_data = result['lead_data']
            current_state = result['current_state']
            qualification_status = result['qualification_status']
            recommendations = result['recommendations']
            
            print(f"🤖 Состояние: {current_state.value}")
            print(f"📊 Статус: {qualification_status.value}")
            
            # Показываем собранные данные
            extracted_info = []
            if lead_data.business_sphere:
                extracted_info.append(f"Сфера: {lead_data.business_sphere}")
            if lead_data.automation_goal:
                extracted_info.append(f"Цель: {lead_data.automation_goal.value}")
            if lead_data.budget_max:
                extracted_info.append(f"Бюджет: до ${lead_data.budget_max}")
            if lead_data.technical_requirements:
                extracted_info.append(f"Требования: {', '.join(lead_data.technical_requirements)}")
            
            if extracted_info:
                print(f"📋 Данные: {' | '.join(extracted_info)}")
            
            # Показываем рекомендации
            if recommendations.get('next_questions'):
                print(f"💡 Рекомендации: {recommendations['next_questions'][0]}")
            
            if result.get('should_escalate'):
                print("🔥 ЭСКАЛАЦИЯ: Клиент готов к передаче менеджеру!")
        
        else:
            print(f"❌ Ошибка: {result.get('error')}")
        
        print("-" * 60)
    
    # Получаем финальную аналитику
    print("\n📊 ИТОГОВАЯ АНАЛИТИКА:")
    
    final_lead = await memory_service.get_lead_data(session_id)
    if final_lead:
        print(f"✅ Собрано данных: {_calculate_completeness(final_lead):.1%}")
        print(f"🎯 Статус: {final_lead.qualification_status.value if final_lead.qualification_status else 'не определен'}")
        print(f"📈 Этап: {final_lead.current_dialog_state.value}")
        
        if memory_service._should_escalate(final_lead):
            print("🚨 ГОТОВ К ЭСКАЛАЦИИ")
    
    # Тестируем аналитику
    analytics_summary = await memory_service.get_analytics_summary(session_id)
    if analytics_summary:
        print(f"\n📈 События: {analytics_summary.get('total_events', 0)}")
        print(f"🔄 Полнота данных: {analytics_summary.get('data_completeness', 0):.1%}")
        print(f"⚡ Скор эскалации: {analytics_summary.get('escalation_score', 0):.1%}")

def _calculate_completeness(lead_data):
    """Вычисляет полноту данных"""
    total_fields = 10
    filled = 0
    
    if lead_data.business_sphere: filled += 1
    if lead_data.automation_goal: filled += 1
    if lead_data.budget_max: filled += 1
    if lead_data.technical_requirements: filled += 1
    if lead_data.urgency_level: filled += 1
    if lead_data.qualification_status: filled += 1
    # ... другие поля
    
    return filled / total_fields

if __name__ == "__main__":
    asyncio.run(test_memory_system())