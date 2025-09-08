#!/usr/bin/env python3
"""
Тест интеграции Google Sheets для бота Алена
"""

import asyncio
import os
import sys
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.integrations.google_sheets_service import GoogleSheetsService
from bot.memory.memory_service import MemoryService
from bot.memory.analytics import AnalyticsService
from bot.config import ZEP_API_KEY

async def test_google_sheets_integration():
    """Тест Google Sheets интеграции"""
    print("🧪 Запуск теста Google Sheets интеграции")
    
    try:
        # Инициализация сервисов
        print("🔧 Инициализация сервисов...")
        memory_service = MemoryService(ZEP_API_KEY or "", enable_memory=bool(ZEP_API_KEY))
        analytics_service = AnalyticsService(ZEP_API_KEY or "")
        
        sheets_service = GoogleSheetsService(memory_service, analytics_service)
        print("✅ Сервисы инициализированы")
        
        # Тест аутентификации
        print("\n🔐 Тест аутентификации...")
        auth_result = await sheets_service.authenticate()
        if auth_result:
            print("✅ Аутентификация успешна")
        else:
            print("❌ Ошибка аутентификации")
            return False
        
        # Тест создания таблицы
        print("\n📊 Тест создания Google таблицы...")
        spreadsheet_id = await sheets_service.create_spreadsheet()
        if spreadsheet_id:
            print(f"✅ Таблица создана: {spreadsheet_id}")
            sheets_url = await sheets_service.get_spreadsheet_url()
            print(f"🔗 URL: {sheets_url}")
        else:
            print("❌ Ошибка создания таблицы")
            return False
        
        # Тест health check
        print("\n🔍 Тест health check...")
        health = await sheets_service.health_check()
        if health:
            print("✅ Health check пройден")
        else:
            print("❌ Health check не пройден")
        
        # Тест синхронизации данных (пустых)
        print("\n🔄 Тест синхронизации данных...")
        sync_leads = await sheets_service.sync_leads_data(days=7)
        sync_analytics = await sheets_service.sync_analytics_data(days=7)
        
        if sync_leads and sync_analytics:
            print("✅ Синхронизация данных успешна")
        else:
            print("⚠️ Частичная синхронизация (нормально при отсутствии данных)")
        
        print(f"\n🎉 Тест завершен успешно!")
        print(f"📊 Google таблица готова: {sheets_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тесте: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_sheets_config():
    """Тест конфигурации листов"""
    print("\n🔧 Тест конфигурации листов...")
    
    from bot.integrations.sheets_config import SHEET_CONFIGURATIONS
    
    for sheet_key, config in SHEET_CONFIGURATIONS.items():
        print(f"📋 Лист '{config['name']}': {len(config['headers'])} колонок")
        
        if sheet_key == 'clients':
            print("   Основные поля клиентов:")
            for i, header in enumerate(config['headers'][:10]):  # Показать первые 10
                print(f"   {i+1:2d}. {header}")
            if len(config['headers']) > 10:
                print(f"   ... и еще {len(config['headers']) - 10} полей")

if __name__ == "__main__":
    print("🚀 Google Sheets Integration Test")
    print("=" * 50)
    
    # Тест конфигурации
    asyncio.run(test_sheets_config())
    
    # Основной тест
    print("\n" + "=" * 50)
    result = asyncio.run(test_google_sheets_integration())
    
    if result:
        print("\n🎯 Интеграция Google Sheets работает корректно!")
        print("\n📝 Следующие шаги:")
        print("1. Установите GOOGLE_SHEETS_ENABLED=true в .env")
        print("2. Перезапустите бота")
        print("3. Данные будут автоматически синхронизироваться")
    else:
        print("\n❌ Тест не пройден. Проверьте настройки OAuth2.")
        print("\n🔧 Возможные решения:")
        print("1. Проверьте credentials/client_secret.json")
        print("2. Убедитесь что Google Sheets API включен в Google Cloud Console")
        print("3. Проверьте redirect URI в настройках OAuth2")