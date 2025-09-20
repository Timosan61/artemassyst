#!/usr/bin/env python3
"""
Тестовый скрипт для проверки смены состояний диалога и сохранения в ZEP
"""
import asyncio
import logging
from datetime import datetime
from typing import List, Tuple

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Импортируем нашего агента
from bot.agent import AlenaAgent
from bot.memory.models import DialogState, ClientType

# Тестовые сообщения для полного прохождения всех состояний
TEST_MESSAGES = [
    # S0_GREETING -> S1_BUSINESS
    ("Для себя хочу купить", "S0_GREETING -> S1_BUSINESS (цель покупки)"),

    # S1_BUSINESS -> S2_GOAL
    ("Я из Москвы, в Сочи не был", "S1_BUSINESS -> S2_GOAL (город указан)"),

    # S2_GOAL -> S3_PAYMENT
    ("Для постоянного проживания ищу", "S2_GOAL -> S3_PAYMENT (цель определена)"),

    # S3_PAYMENT -> S4_REQUIREMENTS
    ("Ипотека от Сбербанка будет", "S3_PAYMENT -> S4_REQUIREMENTS (способ оплаты)"),

    # S4_REQUIREMENTS -> S5_BUDGET
    ("Хочу квартиру в Красной Поляне с видом на горы", "S4_REQUIREMENTS -> S5_BUDGET (локация и тип)"),

    # S5_BUDGET -> S6_URGENCY
    ("Бюджет от 15 до 20 миллионов рублей", "S5_BUDGET -> S6_URGENCY (бюджет определен)"),

    # S6_URGENCY -> S7_EXPERIENCE
    ("Планирую приехать в феврале 2025", "S6_URGENCY -> S7_EXPERIENCE (срочность)"),

    # S7_EXPERIENCE -> S8_ACTION
    ("В Сочи никогда не покупал, первый раз", "S7_EXPERIENCE -> S8_ACTION (опыт)"),

    # S8_ACTION - финальное состояние
    ("Да, готов к онлайн-показу", "S8_ACTION (готовность к показу)"),
]

async def test_dialog_flow():
    """Тестируем полный цикл диалога с проверкой состояний"""

    print("=" * 80)
    print("🧪 ТЕСТИРОВАНИЕ СМЕНЫ СОСТОЯНИЙ ДИАЛОГА")
    print("=" * 80)

    # Создаем агента
    agent = AlenaAgent()

    # Уникальный session_id для теста
    test_session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    test_user_name = "Тестовый Пользователь"

    print(f"\n📝 Session ID: {test_session_id}")
    print(f"👤 Пользователь: {test_user_name}\n")

    # Сохраняем историю для анализа
    dialog_history = []

    for i, (user_message, expected_transition) in enumerate(TEST_MESSAGES, 1):
        print(f"\n{'='*60}")
        print(f"📨 Сообщение {i}/{len(TEST_MESSAGES)}")
        print(f"{'='*60}")
        print(f"👤 USER: {user_message}")
        print(f"📊 Ожидаемый переход: {expected_transition}")

        try:
            # Отправляем сообщение и получаем ответ
            bot_response = await agent.generate_response(
                user_message=user_message,
                session_id=test_session_id,
                user_name=test_user_name,
                existing_session_id=test_session_id  # Важно! Используем тот же session_id
            )

            print(f"\n🤖 BOT: {bot_response[:200]}...")

            # Получаем текущее состояние из памяти
            memory_insights = await agent.get_memory_insights(test_session_id)

            if memory_insights:
                current_state = memory_insights.get('current_state', 'unknown')
                qualification = memory_insights.get('qualification_status', 'unknown')
                lead_data = memory_insights.get('lead_data', {})

                print(f"\n📍 Текущее состояние: {current_state}")
                print(f"🎯 Квалификация: {qualification}")

                # Выводим ключевые собранные данные
                if lead_data:
                    print(f"\n📋 Собранные данные:")
                    if lead_data.get('name'):
                        print(f"  • Имя: {lead_data['name']}")
                    if lead_data.get('city'):
                        print(f"  • Город: {lead_data['city']}")
                    if lead_data.get('automation_goal'):
                        print(f"  • Цель: {lead_data['automation_goal']}")
                    if lead_data.get('payment_type'):
                        print(f"  • Оплата: {lead_data['payment_type']}")
                    if lead_data.get('preferred_locations'):
                        print(f"  • Локации: {', '.join(lead_data['preferred_locations'])}")
                    if lead_data.get('property_type'):
                        print(f"  • Тип недвижимости: {lead_data['property_type']}")
                    if lead_data.get('budget_min') or lead_data.get('budget_max'):
                        print(f"  • Бюджет: {lead_data.get('budget_min', 0)}-{lead_data.get('budget_max', '∞')}")
                    if lead_data.get('urgency_date'):
                        print(f"  • Срочность: {lead_data['urgency_date']}")
                    if lead_data.get('sochi_experience'):
                        print(f"  • Опыт в Сочи: {lead_data['sochi_experience']}")

            # Сохраняем в историю
            dialog_history.append({
                'message_num': i,
                'user': user_message,
                'bot': bot_response[:100],
                'state': current_state,
                'qualification': qualification
            })

            # Небольшая задержка между сообщениями
            await asyncio.sleep(1)

        except Exception as e:
            print(f"\n❌ ОШИБКА: {e}")
            logger.error(f"Ошибка при обработке сообщения {i}: {e}")

    # Итоговый отчет
    print(f"\n{'='*80}")
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print(f"{'='*80}\n")

    print("🔄 История состояний:")
    for entry in dialog_history:
        print(f"  {entry['message_num']}. {entry['state']} ({entry['qualification']})")

    # Проверяем финальное состояние
    final_insights = await agent.get_memory_insights(test_session_id)
    if final_insights:
        final_state = final_insights.get('current_state', 'unknown')
        final_qualification = final_insights.get('qualification_status', 'unknown')
        should_escalate = final_insights.get('should_escalate', False)

        print(f"\n✅ Финальное состояние: {final_state}")
        print(f"✅ Финальная квалификация: {final_qualification}")
        print(f"✅ Требуется эскалация: {'ДА 🔥' if should_escalate else 'НЕТ'}")

        # Проверка корректности
        if final_state == 'S8_ACTION':
            print("\n🎉 ТЕСТ ПРОЙДЕН! Достигнуто финальное состояние S8_ACTION")
        else:
            print(f"\n⚠️ ТЕСТ НЕ ПРОЙДЕН! Ожидалось S8_ACTION, получено {final_state}")

async def test_state_persistence():
    """Тест на сохранение состояния между сообщениями"""

    print("\n" + "=" * 80)
    print("🧪 ТЕСТ СОХРАНЕНИЯ СОСТОЯНИЯ")
    print("=" * 80)

    agent = AlenaAgent()
    test_session_id = f"persistence_test_{datetime.now().strftime('%H%M%S')}"

    # Отправляем первое сообщение
    print("\n1️⃣ Первое сообщение...")
    response1 = await agent.generate_response(
        "Для себя ищу",
        test_session_id,
        "Тест Persistence"
    )

    insights1 = await agent.get_memory_insights(test_session_id)
    state1 = insights1.get('current_state', 'unknown')
    print(f"Состояние после 1-го сообщения: {state1}")

    # Ждем 2 секунды
    await asyncio.sleep(2)

    # Отправляем второе сообщение
    print("\n2️⃣ Второе сообщение...")
    response2 = await agent.generate_response(
        "Я из Волгограда",
        test_session_id,
        "Тест Persistence",
        existing_session_id=test_session_id  # Используем тот же session_id
    )

    insights2 = await agent.get_memory_insights(test_session_id)
    state2 = insights2.get('current_state', 'unknown')
    print(f"Состояние после 2-го сообщения: {state2}")

    # Проверяем, что бот не здоровается повторно
    if "Здравствуйте" in response2 or "Я Алена" in response2:
        print("\n❌ ОШИБКА: Бот снова здоровается! Состояние потеряно!")
        print(f"Ответ бота: {response2[:200]}")
    else:
        print("\n✅ Состояние сохранено! Бот продолжает диалог")
        print(f"Ответ бота: {response2[:200]}")

async def main():
    """Запуск всех тестов"""

    print("\n🚀 ЗАПУСК ТЕСТИРОВАНИЯ СИСТЕМЫ СОСТОЯНИЙ\n")

    # Тест полного цикла диалога
    await test_dialog_flow()

    # Тест сохранения состояния
    await test_state_persistence()

    print("\n✅ Тестирование завершено!\n")

if __name__ == "__main__":
    asyncio.run(main())