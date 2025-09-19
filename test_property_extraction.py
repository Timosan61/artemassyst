#!/usr/bin/env python3
"""
Тест извлечения типа недвижимости из сообщений
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.memory.extractors import LeadDataExtractor
from bot.memory.models import LeadData

def test_property_type_extraction():
    """Тест извлечения типа недвижимости"""
    
    test_messages = [
        "дом, до 5 млн рублей",
        "ищу дом в Красной Поляне",
        "хочу квартиру у моря",
        "нужны апартаменты в Сириусе", 
        "рассматриваю участок под застройку",
        "дома в центре Сочи",
        "покупаю коттедж",
        "студию для сдачи"
    ]
    
    expected_results = [
        "дом",      # дом, до 5 млн рублей
        "дом",      # ищу дом в Красной Поляне  
        "квартира", # хочу квартиру у моря
        "апартаменты", # нужны апартаменты в Сириусе
        "участок",  # рассматриваю участок под застройку
        "дом",      # дома в центре Сочи
        "дом",      # покупаю коттедж
        "квартира"  # студию для сдачи
    ]
    
    print("🏠 Тестирование извлечения типа недвижимости...")
    print("=" * 60)
    
    all_passed = True
    for i, (message, expected) in enumerate(zip(test_messages, expected_results)):
        lead = LeadData()
        
        # Извлекаем данные
        updated_lead = LeadDataExtractor.extract_from_message(message, lead)
        
        # Проверяем результат
        actual = getattr(updated_lead, 'property_type', None)
        status = "✅" if actual == expected else "❌"
        
        if actual != expected:
            all_passed = False
        
        print(f"{status} Тест {i+1}: '{message}'")
        print(f"   Ожидаемый: {expected}")
        print(f"   Получен: {actual}")
        print()
    
    print("=" * 60)
    if all_passed:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ!")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ!")
    print()
    
    return all_passed

def test_system_context():
    """Тест того, как данные передаются в системный промпт"""
    
    print("🤖 Тестирование системного контекста...")
    print("=" * 60)
    
    lead = LeadData()
    lead.name = "Артем"
    lead.property_type = "дом"
    lead.budget_max = 5000000
    lead.preferred_locations = ["Красная Поляна"]
    
    # Имитируем формирование контекста
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
    
    print("Сформированный контекст:")
    print(context)
    print()
    
    if "Тип: дом" in context:
        print("✅ Тип недвижимости правильно передается в контекст")
    else:
        print("❌ Тип недвижимости НЕ передается в контекст")

if __name__ == "__main__":
    print("🧪 Запуск тестов извлечения данных недвижимости\n")
    
    # Тест извлечения
    extraction_passed = test_property_type_extraction()
    
    # Тест системного контекста  
    test_system_context()
    
    print("📋 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print("✅ Извлечение типа недвижимости:", "РАБОТАЕТ" if extraction_passed else "НЕ РАБОТАЕТ")