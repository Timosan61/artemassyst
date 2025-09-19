#!/usr/bin/env python3
"""
Комплексное тестирование всей системы предотвращения повторяющихся вопросов
"""
import asyncio
import os
import uuid
import time
from datetime import datetime
from dotenv import load_dotenv
from bot.memory.memory_service import MemoryService
from bot.memory.session_manager import session_manager

# Загружаем переменные окружения
load_dotenv()

async def test_realistic_conversation():
    """Тест реалистичного диалога с проверкой повторов"""

    # Получаем ZEP API ключ
    zep_api_key = os.getenv('ZEP_API_KEY')
    if not zep_api_key:
        print("❌ ZEP_API_KEY не найден")
        return

    print(f"🔑 Используем ZEP API Key: {zep_api_key[:8]}...{zep_api_key[-4:]}")

    # Инициализируем сервис памяти
    memory_service = MemoryService(zep_api_key, enable_memory=True)
    print("✅ MemoryService инициализирован")

    # Создаем тестового пользователя
    test_user_id = f"user_{uuid.uuid4().hex[:8]}"
    test_chat_id = f"chat_{uuid.uuid4().hex[:8]}"
    print(f"🆔 Тестовый пользователь: {test_user_id}")
    print(f"💬 Тестовый чат: {test_chat_id}")

    # Реалистичный сценарий диалога
    conversation_scenario = [
        # Первое сообщение - приветствие
        {"text": "Привет!", "role": "user", "expect_questions": True},
        {"text": "Здравствуйте! Ищете недвижимость для себя или как инвестицию?", "role": "assistant", "expect_questions": False},

        # Пользователь отвечает и задает вопрос
        {"text": "Для себя, хочу переехать в Сочи", "role": "user", "expect_questions": True},
        {"text": "Отлично! Для ПМЖ отличный выбор. Какую недвижимость рассматриваете?", "role": "assistant", "expect_questions": False},

        # Пользователь уточняет детали
        {"text": "Дом, 2-3 этажа, в Красной Поляне", "role": "user", "expect_questions": True},
        {"text": "Понял, дом в Красной Поляне. На какой бюджет ориентируемся?", "role": "assistant", "expect_questions": False},

        # Пользователь называет бюджет
        {"text": "До 5 миллионов рублей", "role": "user", "expect_questions": True},
        {"text": "Отлично! Есть несколько вариантов. Когда планируете приехать на просмотр?", "role": "assistant", "expect_questions": False},

        # Пользователь возвращается к разговору позже (проверка повторов)
        {"text": "Привет, ты меня помнишь?", "role": "user", "expect_questions": False},  # НЕ должно быть повторов
        {"text": "Конечно помню! Мы с вами обсуждали дом в Красной Поляне до 5 миллионов. Когда вы планируете приехать на просмотр?", "role": "assistant", "expect_questions": False},

        # Пользователь спрашивает о том, что уже обсуждали (проверка)
        {"text": "А какой у нас был бюджет?", "role": "user", "expect_questions": False},
        {"text": "Мы с вами определили бюджет до 5 миллионов рублей. Все верно?", "role": "assistant", "expect_questions": False},

        # Пользователь уточняет детали
        {"text": "Да, все верно. А где именно в Красной Поляне?", "role": "user", "expect_questions": True},
        {"text": "Есть варианты в Эсто-Садоке и на Розе Хутор. Какая локация вам ближе?", "role": "assistant", "expect_questions": False},
    ]

    print(f"\n📝 Начинаем тест реалистичного диалога...")
    print("=" * 70)

    session_id = None
    duplicate_questions_found = 0
    total_questions_asked = 0

    for i, message_data in enumerate(conversation_scenario):
        print(f"\n--- Этап {i+1}: {message_data['role']} ---")
        print(f"📨 Сообщение: '{message_data['text']}'")

        try:
            # Получаем или создаем сессию
            if session_id is None:
                session_id = session_manager.generate_session_id(test_user_id, test_chat_id)
                print(f"🆔 Создана новая сессия: {session_id}")

            # Обрабатываем сообщение
            result = await memory_service.process_message(
                user_id=test_user_id,
                message_text=message_data['text'],
                message_type=message_data['role'],
                chat_id=test_chat_id,
                existing_session_id=session_id
            )

            if result.get('success'):
                lead_data = result.get('lead_data')
                current_state = result.get('current_state')
                recommendations = result.get('recommendations', {})

                print(f"✅ Успешно обработано")
                print(f"   📊 Состояние: {current_state}")

                # Проверяем рекомендованные вопросы
                next_questions = recommendations.get('next_questions', [])
                if next_questions:
                    print(f"   ❓ Рекомендованные вопросы:")
                    for j, question in enumerate(next_questions):
                        print(f"      {j+1}. {question}")
                        total_questions_asked += 1

                        # Проверяем на повторы
                        if lead_data and question in lead_data.asked_questions[:-1]:  # Кроме последнего
                            duplicate_questions_found += 1
                            print(f"      ⚠️ ОБНАРУЖЕН ПОВТОР: '{question}' уже задавали ранее!")

                # Проверяем ожидания
                if message_data['expect_questions'] and not next_questions:
                    print(f"   ⚠️ ОЖИДАЛИСЬ вопросы, но их нет!")
                elif not message_data['expect_questions'] and next_questions:
                    print(f"   ⚠️ НЕ ОЖИДАЛИСЬ вопросы, но они есть!")

                # Показываем собранные данные
                if lead_data:
                    data_parts = []
                    if lead_data.automation_goal:
                        data_parts.append(f"Цель: {lead_data.automation_goal.value}")
                    if lead_data.budget_max:
                        data_parts.append(f"Бюджет: до {lead_data.budget_max}")
                    if lead_data.property_type:
                        data_parts.append(f"Тип: {lead_data.property_type}")
                    if lead_data.preferred_locations:
                        data_parts.append(f"Локации: {lead_data.preferred_locations}")

                    if data_parts:
                        print(f"   📊 Данные: {' | '.join(data_parts)}")

                    # Показываем историю вопросов
                    if lead_data.asked_questions:
                        print(f"   📋 История вопросов ({len(lead_data.asked_questions)}):")
                        # Показываем последние 3 вопроса
                        for j, question in enumerate(lead_data.asked_questions[-3:], 1):
                            print(f"      - {question}")

            else:
                print(f"❌ Ошибка: {result.get('error')}")

        except Exception as e:
            print(f"❌ Исключение: {e}")

        # Небольшая задержка между сообщениями для реалистичности
        await asyncio.sleep(0.5)

    print(f"\n🏁 === ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ ТЕСТА ===")
    print("=" * 70)

    # Проверяем финальные данные
    final_lead = await memory_service.get_lead_data(session_id)
    if final_lead:
        print(f"📋 Финальные данные лида:")
        print(f"   - Состояние диалога: {final_lead.current_dialog_state}")
        print(f"   - Всего заданных вопросов: {len(final_lead.asked_questions)}")
        print(f"   - Последний вопрос: {final_lead.last_question_asked}")

        # Проверяем на повторяющиеся вопросы
        unique_questions = set(final_lead.asked_questions)
        if len(final_lead.asked_questions) != len(unique_questions):
            print(f"❌ НАЙДЕНЫ ПОВТОРЯЮЩИЕСЯ ВОПРОСЫ!")
            print(f"   - Всего вопросов: {len(final_lead.asked_questions)}")
            print(f"   - Уникальных: {len(unique_questions)}")
            print(f"   - Повторов: {len(final_lead.asked_questions) - len(unique_questions)}")
        else:
            print(f"✅ ПОВТОРЯЮЩИХСЯ ВОПРОСОВ НЕ НАЙДЕНО!")

    # Статистика сессии
    session_stats = session_manager.get_session_stats()
    print(f"\n📊 Статистика сессий:")
    print(f"   - Всего сессий: {session_stats['total_sessions']}")
    print(f"   - Активных сессий: {session_stats['active_sessions']}")
    print(f"   - Среднее количество вопросов: {total_questions_asked}")

    # Итоговая оценка
    print(f"\n🎯 ИТОГИ:")
    if duplicate_questions_found == 0:
        print(f"✅ СИСТЕМА РАБОТАЕТ ОТЛИЧНО! Повторяющихся вопросов нет.")
        return True
    else:
        print(f"❌ НАЙДЕНО {duplicate_questions_found} повторяющихся вопросов!")
        return False

async def test_multiple_users():
    """Тест с несколькими пользователями одновременно"""

    print(f"\n🧪 Тестирование нескольких пользователей...")
    print("=" * 70)

    zep_api_key = os.getenv('ZEP_API_KEY')
    if not zep_api_key:
        print("❌ ZEP_API_KEY не найден")
        return False

    memory_service = MemoryService(zep_api_key, enable_memory=True)

    # Создаем несколько пользователей
    users = [
        {"user_id": f"user_{uuid.uuid4().hex[:8]}", "chat_id": f"chat_{uuid.uuid4().hex[:8]}", "name": "Алексей"},
        {"user_id": f"user_{uuid.uuid4().hex[:8]}", "chat_id": f"chat_{uuid.uuid4().hex[:8]}", "name": "Мария"},
        {"user_id": f"user_{uuid.uuid4().hex[:8]}", "chat_id": f"chat_{uuid.uuid4().hex[:8]}", "name": "Дмитрий"},
    ]

    async def process_user(user_data):
        """Обрабатывает одного пользователя"""
        session_id = session_manager.generate_session_id(user_data["user_id"], user_data["chat_id"])

        messages = [
            f"Привет, меня зовут {user_data['name']}",
            "Хочу купить недвижимость в Сочи",
            "Дом, до 3 миллионов",
            "В Красной Поляне",
        ]

        user_questions = []

        for message in messages:
            result = await memory_service.process_message(
                user_id=user_data["user_id"],
                message_text=message,
                message_type="user",
                chat_id=user_data["chat_id"],
                existing_session_id=session_id
            )

            if result.get('success'):
                recommendations = result.get('recommendations', {})
                questions = recommendations.get('next_questions', [])
                user_questions.extend(questions)

        return user_questions

    # Обрабатываем всех пользователей параллельно
    results = await asyncio.gather(
        *[process_user(user) for user in users]
    )

    print(f"📊 Результаты по пользователям:")
    total_questions = 0
    total_duplicates = 0

    for i, (user_data, questions) in enumerate(zip(users, results)):
        unique_questions = set(questions)
        duplicates = len(questions) - len(unique_questions)

        print(f"   {user_data['name']}: {len(questions)} вопросов, {duplicates} повторов")
        total_questions += len(questions)
        total_duplicates += duplicates

    print(f"\n📈 Общая статистика:")
    print(f"   - Всего вопросов: {total_questions}")
    print(f"   - Повторов: {total_duplicates}")
    print(f"   - Уникальных: {total_questions - total_duplicates}")

    return total_duplicates == 0

async def main():
    """Главная функция тестирования"""
    print("🚀 Комплексное тестирование системы предотвращения повторяющихся вопросов")
    print("=" * 80)

    # Тест 1: Реалистичный диалог
    test1_passed = await test_realistic_conversation()

    # Тест 2: Несколько пользователей
    test2_passed = await test_multiple_users()

    print(f"\n🏆 ОБЩИЕ РЕЗУЛЬТАТЫ:")
    print("=" * 80)

    if test1_passed and test2_passed:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ Система предотвращения повторяющихся вопросов работает отлично!")
    else:
        print("❌ ЕСТЬ ПРОБЛЕМЫ!")
        if not test1_passed:
            print("❌ Провален тест реалистичного диалога")
        if not test2_passed:
            print("❌ Провален тест многопользовательского сценария")

if __name__ == "__main__":
    asyncio.run(main())