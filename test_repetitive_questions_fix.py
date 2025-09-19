#!/usr/bin/env python3
"""
Тестирование исправлений для предотвращения повторяющихся вопросов
"""
import asyncio
import os
import uuid
from dotenv import load_dotenv
from bot.memory.memory_service import MemoryService
from bot.memory.session_manager import session_manager

# Загружаем переменные окружения
load_dotenv()

async def test_repetitive_questions_fix():
    """Тестирует предотвращение повторяющихся вопросов"""

    # Получаем ZEP API ключ
    zep_api_key = os.getenv('ZEP_API_KEY')
    if not zep_api_key:
        print("❌ ZEP_API_KEY не найден")
        return

    print(f"🔑 Используем ZEP API Key: {zep_api_key[:8]}...{zep_api_key[-4:]}")

    # Инициализируем сервис памяти
    memory_service = MemoryService(zep_api_key, enable_memory=True)
    print("✅ MemoryService инициализирован")

    # Создаем тестовую сессию
    test_user_id = f"test_user_{uuid.uuid4().hex[:8]}"
    test_session_id = session_manager.generate_session_id(test_user_id)
    print(f"🆔 Создана тестовая сессия: {test_session_id}")

    # Тестовый сценарий с повторяющимися вопросами
    test_messages = [
        # Первый цикл - собираем информацию
        ("привет", "user"),
        ("Здравствуйте! Ищете недвижимость для себя или как инвестицию?", "assistant"),
        ("для себя", "user"),
        ("Понятно, для себя. Какая цель покупки?", "assistant"),
        ("пмж", "user"),
        ("Отлично, для ПМЖ. Какую недвижимость рассматриваете?", "assistant"),
        ("дом в красной поляне", "user"),

        # Второй цикл - проверяем повторение вопросов
        ("привет", "user"),  # Повтор приветствия
        ("Здравствуйте! Ищете недвижимость для себя или как инвестицию?", "assistant"),
        ("я же уже сказал для себя", "user"),
        ("Извините, действительно. Какую недвижимость рассматриваете?", "assistant"),
    ]

    print(f"\n📝 Начинаем тестирование предотвращения повторяющихся вопросов...")

    asked_questions_history = []

    for i, (message, msg_type) in enumerate(test_messages):
        print(f"\n--- Шаг {i+1}: {msg_type} ---")
        print(f"📨 '{message}'")

        try:
            result = await memory_service.process_message(
                user_id=test_user_id,
                message_text=message,
                message_type=msg_type,
                existing_session_id=test_session_id
            )

            if result.get('success'):
                lead_data = result.get('lead_data')
                current_state = result.get('current_state')
                recommendations = result.get('recommendations', {})

                print(f"✅ Успешно обработано")
                print(f"   📊 Состояние: {current_state}")

                # Показываем рекомендованные вопросы
                next_questions = recommendations.get('next_questions', [])
                if next_questions:
                    print(f"   ❓ Рекомендованные вопросы:")
                    for j, question in enumerate(next_questions):
                        print(f"      {j+1}. {question}")
                        asked_questions_history.append(question)

                # Показываем историю заданных вопросов из LeadData
                if lead_data and lead_data.asked_questions:
                    print(f"   📋 История заданных вопросов ({len(lead_data.asked_questions)}):")
                    for j, question in enumerate(lead_data.asked_questions[-3:], 1):  # Последние 3
                        print(f"      - {question}")

                # Показываем собранные данные
                if lead_data:
                    data_parts = []
                    if lead_data.automation_goal:
                        data_parts.append(f"Цель: {lead_data.automation_goal.value}")
                    if lead_data.property_type:
                        data_parts.append(f"Тип: {lead_data.property_type}")
                    if lead_data.preferred_locations:
                        data_parts.append(f"Локации: {lead_data.preferred_locations}")

                    if data_parts:
                        print(f"   📊 Данные: {' | '.join(data_parts)}")

            else:
                print(f"❌ Ошибка: {result.get('error')}")

        except Exception as e:
            print(f"❌ Исключение: {e}")

    print(f"\n🏁 === РЕЗУЛЬТАТЫ ТЕСТА ===")

    # Проверяем статистику сессии
    session_stats = session_manager.get_session_stats()
    print(f"📊 Статистика сессий:")
    print(f"   - Всего сессий: {session_stats['total_sessions']}")
    print(f"   - Среднее количество вопросов на сессию: {session_stats['avg_questions_per_session']:.1f}")

    # Проверяем историю вопросов в сессии
    session_info = session_manager.get_session_info(test_session_id)
    if session_info:
        print(f"\n📋 Информация о тестовой сессии:")
        print(f"   - User ID: {session_info['user_id']}")
        print(f"   - Создана: {session_info['created_at']}")
        print(f"   - Последняя активность: {session_info['last_activity']}")
        print(f"   - Заданные вопросы: {len(session_info['question_history'])}")

    # Проверяем финальные данные
    final_lead = await memory_service.get_lead_data(test_session_id)
    if final_lead:
        print(f"\n📋 Финальные данные лида:")
        print(f"   - Состояние диалога: {final_lead.current_dialog_state}")
        print(f"   - Заданные вопросы: {len(final_lead.asked_questions)}")
        print(f"   - Последний вопрос: {final_lead.last_question_asked}")

        # Проверяем на повторяющиеся вопросы
        unique_questions = set(final_lead.asked_questions)
        if len(final_lead.asked_questions) != len(unique_questions):
            print(f"❌ Найдены повторяющиеся вопросы!")
            print(f"   - Всего вопросов: {len(final_lead.asked_questions)}")
            print(f"   - Уникальных: {len(unique_questions)}")
        else:
            print(f"✅ Повторяющихся вопросов не найдено!")

    print(f"\n✅ Тест завершен!")

if __name__ == "__main__":
    asyncio.run(test_repetitive_questions_fix())