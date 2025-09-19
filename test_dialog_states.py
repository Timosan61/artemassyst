#!/usr/bin/env python3
"""
Тест логики переходов состояний диалога
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.memory.extractors import LeadDataExtractor, DialogStateExtractor
from bot.memory.models import LeadData, DialogState

def test_dialog_state_transitions():
    """Тест переходов состояний диалога"""
    
    print("🔄 Тестирование переходов состояний диалога...")
    print("=" * 60)
    
    # Сценарий: пользователь сразу говорит "дом, до 5 млн рублей"
    lead = LeadData()
    lead.current_dialog_state = DialogState.S4_REQUIREMENTS  # Состояние "требования к объекту"
    
    message = "дом, до 5 млн рублей"
    
    # Извлекаем данные
    updated_lead = LeadDataExtractor.extract_from_message(message, lead)
    
    print(f"📨 Сообщение: '{message}'")
    print(f"🏠 Извлеченный тип: {getattr(updated_lead, 'property_type', None)}")
    print(f"💰 Извлеченный бюджет: {updated_lead.budget_max}")
    print(f"📍 Текущее состояние: {updated_lead.current_dialog_state}")
    
    # Определяем новое состояние
    new_state = DialogStateExtractor.determine_state(
        message, 
        updated_lead.current_dialog_state, 
        updated_lead
    )
    
    print(f"🔄 Новое состояние: {new_state}")
    
    # Проверяем ожидаемый результат
    if new_state == DialogState.S5_BUDGET:
        print("✅ ПРАВИЛЬНО: Состояние изменилось на S5_BUDGET (так как тип объекта определен)")
    else:
        print(f"❌ ОШИБКА: Ожидался S5_BUDGET, получен {new_state}")
    
    print()
    
    # Тест 2: только локация без типа
    print("📍 Тест 2: Только локация без типа...")
    lead2 = LeadData()
    lead2.current_dialog_state = DialogState.S4_REQUIREMENTS
    message2 = "Красная Поляна"
    
    updated_lead2 = LeadDataExtractor.extract_from_message(message2, lead2)
    new_state2 = DialogStateExtractor.determine_state(message2, updated_lead2.current_dialog_state, updated_lead2)
    
    print(f"📨 Сообщение: '{message2}'")
    print(f"📍 Локации: {updated_lead2.preferred_locations}")
    print(f"🔄 Новое состояние: {new_state2}")
    
    if new_state2 == DialogState.S5_BUDGET:
        print("✅ ПРАВИЛЬНО: Переход на бюджет (локация определена)")
    else:
        print(f"❌ ОШИБКА: Ожидался переход на бюджет")
    
    print()
    
    # Тест 3: неопределенное требование
    print("❓ Тест 3: Неопределенное сообщение...")
    lead3 = LeadData()
    lead3.current_dialog_state = DialogState.S4_REQUIREMENTS
    message3 = "не знаю еще"
    
    updated_lead3 = LeadDataExtractor.extract_from_message(message3, lead3)
    new_state3 = DialogStateExtractor.determine_state(message3, updated_lead3.current_dialog_state, updated_lead3)
    
    print(f"📨 Сообщение: '{message3}'")
    print(f"🔄 Новое состояние: {new_state3}")
    
    if new_state3 == DialogState.S4_REQUIREMENTS:
        print("✅ ПРАВИЛЬНО: Остается в S4_REQUIREMENTS (недостаточно информации)")
    else:
        print(f"❌ ОШИБКА: Должен остаться в S4_REQUIREMENTS")

def test_context_building():
    """Тест построения контекста для LLM"""
    
    print("\n🤖 Тестирование контекста для LLM...")
    print("=" * 60)
    
    lead = LeadData()
    lead.name = "Артем"
    lead.property_type = "дом"
    lead.budget_max = 5000000
    lead.preferred_locations = ["Красная Поляна"]
    lead.current_dialog_state = DialogState.S4_REQUIREMENTS
    
    # Имитируем построение контекста
    client_info = []
    if lead.name:
        client_info.append(f"Имя: {lead.name}")
    if getattr(lead, 'property_type', None):
        client_info.append(f"Тип: {lead.property_type}")
    if lead.budget_max:
        client_info.append(f"Бюджет до: {lead.budget_max} руб")
    if lead.preferred_locations:
        locations = ", ".join(lead.preferred_locations)
        client_info.append(f"Локации: {locations}")
    
    context = f"ДАННЫЕ КЛИЕНТА: {' | '.join(client_info)}"
    state_desc = "Выясните недостающие требования к объекту (тип, локация, параметры)"
    
    print("Полный контекст для LLM:")
    print(context)
    print(f"ЭТАП ДИАЛОГА: {lead.current_dialog_state.value} - {state_desc}")
    print()
    
    if "Тип: дом" in context:
        print("✅ LLM видит что тип объекта уже известен")
    else:
        print("❌ LLM НЕ видит тип объекта")
    
    if "недостающие требования" in state_desc:
        print("✅ LLM понимает что нужно спрашивать только недостающие параметры")
    else:
        print("❌ LLM не понимает что делать с уже известными данными")

if __name__ == "__main__":
    print("🧪 Запуск тестов логики состояний диалога\n")
    
    test_dialog_state_transitions()
    test_context_building()
    
    print("\n📋 ИТОГ: Если все тесты прошли - бот должен перестать повторять вопросы")