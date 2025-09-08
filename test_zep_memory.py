#!/usr/bin/env python3
"""
Тест интеграции с ZEP Cloud для системы памяти бота Алена
"""
import asyncio
import logging
import os
import sys
from datetime import datetime
from bot.config import ZEP_API_KEY
from bot.memory.analytics import AnalyticsService

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_analytics_service():
    """Тестирует AnalyticsService с ZEP Cloud"""
    print("\n🧪 Тестируем AnalyticsService с ZEP Cloud...")
    
    if not ZEP_API_KEY:
        print("❌ ZEP_API_KEY не найден в конфигурации")
        return False
    
    print(f"🔑 Используем ZEP API key: {ZEP_API_KEY[:20]}...")
    
    try:
        # Инициализируем сервис аналитики
        analytics = AnalyticsService(ZEP_API_KEY)
        print("✅ AnalyticsService инициализирован")
        
        # Тестовый session_id
        test_session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"🧪 Тестовая сессия: {test_session_id}")
        
        # Тест 1: Сохранение события
        print("\n📝 Тест 1: Сохранение тестового события...")
        await analytics.track_event(
            session_id=test_session_id,
            event_type="test_event",
            event_data={
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "message": "Тестовое событие для проверки ZEP Cloud"
            }
        )
        print("✅ Событие сохранено")
        
        # Тест 2: Сохранение события смены состояния
        print("\n🔄 Тест 2: Сохранение события смены состояния...")
        await analytics.track_event(
            session_id=test_session_id,
            event_type="state_change",
            event_data={
                "from": "s0_greeting",
                "to": "s1_business"
            }
        )
        print("✅ Событие смены состояния сохранено")
        
        # Тест 3: Сохранение события квалификации
        print("\n🎯 Тест 3: Сохранение события квалификации...")
        await analytics.track_event(
            session_id=test_session_id,
            event_type="qualification_change",
            event_data={
                "status": "hot"
            }
        )
        print("✅ Событие квалификации сохранено")
        
        # Ждем немного для индексации
        print("\n⏳ Ждем 10 секунд для индексации в ZEP...")
        await asyncio.sleep(10)
        
        # Тест 4: Получение событий сессии
        print("\n📋 Тест 4: Получение событий сессии...")
        events = await analytics.get_session_events(test_session_id, days=1)
        print(f"✅ Получено {len(events)} событий")
        
        for i, event in enumerate(events):
            print(f"  {i+1}. {event.get('event_type', 'unknown')} - {event.get('timestamp', 'no_timestamp')}")
        
        # Тест 5: Анализ воронки конверсии
        print("\n📊 Тест 5: Анализ воронки конверсии...")
        funnel = await analytics.get_conversion_funnel(days=1)
        print("✅ Воронка конверсии:")
        print(f"  - Всего сессий: {funnel.get('total_sessions', 0)}")
        print(f"  - Смены состояний: {funnel.get('funnel_data', {}).get('s1_business', 0)}")
        print(f"  - Горячие лиды: {funnel.get('funnel_data', {}).get('qualification_hot', 0)}")
        
        # Тест 6: Ежедневная статистика
        print("\n📈 Тест 6: Ежедневная статистика...")
        daily_stats = await analytics.get_daily_stats(days=1)
        print(f"✅ Получена статистика за {len(daily_stats)} дней")
        
        for stats in daily_stats:
            print(f"  - {stats.get('date', 'unknown')}: {stats.get('total_events', 0)} событий, {stats.get('unique_sessions', 0)} сессий")
        
        # Тест 7: Генерация отчета
        print("\n📄 Тест 7: Генерация сводного отчета...")
        report = await analytics.generate_report(days=1)
        print("✅ Отчет сгенерирован:")
        print(f"  - Период: {report.get('period', 'unknown')}")
        summary = report.get('summary', {})
        print(f"  - Всего сессий: {summary.get('total_sessions', 0)}")
        print(f"  - Горячие лиды: {summary.get('hot_leads', 0)}")
        print(f"  - Конверсия в горячие лиды: {summary.get('hot_lead_rate', 0):.1f}%")
        
        recommendations = report.get('recommendations', [])
        print(f"  - Рекомендаций: {len(recommendations)}")
        for rec in recommendations:
            print(f"    • {rec}")
        
        print("\n🎉 Все тесты AnalyticsService прошли успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования AnalyticsService: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_zep_basic_connection():
    """Базовый тест подключения к ZEP Cloud"""
    print("\n🔌 Базовый тест подключения к ZEP Cloud...")
    
    try:
        from zep_cloud.client import Zep
        
        client = Zep(api_key=ZEP_API_KEY)
        
        # Пробуем создать группу
        test_group_id = f"test_group_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        await asyncio.to_thread(
            client.group.add,
            group_id=test_group_id,
            name="Test Group",
            description="Тестовая группа для проверки подключения"
        )
        
        print(f"✅ Группа {test_group_id} создана")
        
        # Добавляем тестовые данные
        test_data = {
            "test": True,
            "timestamp": datetime.now().isoformat(),
            "message": "Тестовое подключение к ZEP Cloud"
        }
        
        await asyncio.to_thread(
            client.graph.add,
            group_id=test_group_id,
            type="json",
            data=str(test_data)
        )
        
        print("✅ Тестовые данные добавлены в граф")
        
        # Ждем индексации
        await asyncio.sleep(5)
        
        # Пробуем поиск
        search_results = await asyncio.to_thread(
            client.graph.search,
            group_id=test_group_id,
            query="test",
            scope="episodes"
        )
        
        episodes_count = len(search_results.episodes) if search_results.episodes else 0
        print(f"✅ Поиск вернул {episodes_count} эпизодов")
        
        print("🎉 Базовое подключение к ZEP Cloud работает!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка базового подключения к ZEP: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов ZEP Cloud интеграции")
    print("=" * 50)
    
    # Проверяем наличие API ключа
    if not ZEP_API_KEY:
        print("❌ ZEP_API_KEY не найден в переменных окружения")
        print("Проверьте файл .env")
        return
    
    print(f"🔑 ZEP API Key: {ZEP_API_KEY[:20]}...")
    
    # Запускаем тесты
    test1_result = await test_zep_basic_connection()
    test2_result = await test_analytics_service()
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"  - Базовое подключение ZEP: {'✅ УСПЕХ' if test1_result else '❌ ОШИБКА'}")
    print(f"  - AnalyticsService: {'✅ УСПЕХ' if test2_result else '❌ ОШИБКА'}")
    
    if test1_result and test2_result:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("ZEP Cloud интеграция работает корректно")
    else:
        print("\n❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛИЛИСЬ")
        print("Проверьте конфигурацию и логи")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()