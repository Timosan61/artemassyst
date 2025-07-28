#!/usr/bin/env python3
"""
🔍 Проверка статуса деплоя на Digital Ocean
"""

import requests
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Digital Ocean App ID
APP_ID = "86f72a9c-8404-4fc5-82c7-081931df3ba9"
DO_TOKEN = os.getenv('DIGITALOCEAN_TOKEN')

headers = {
    'Authorization': f'Bearer {DO_TOKEN}',
    'Content-Type': 'application/json'
}

print("🔍 Проверка статуса деплоя artemmyassyst...")

try:
    # Получить информацию о приложении
    response = requests.get(f'https://api.digitalocean.com/v2/apps/{APP_ID}', headers=headers)
    
    if response.status_code == 200:
        app_data = response.json()['app']
        print(f"✅ Приложение: {app_data['spec']['name']}")
        print(f"📊 Статус: {app_data['phase']}")
        print(f"🌐 Live URL: {app_data['live_url']}")
        
        # Последний деплой
        if 'last_deployment' in app_data:
            deployment = app_data['last_deployment']
            print(f"🚀 Последний деплой: {deployment['id']}")
            print(f"📅 Создан: {deployment['created_at']}")
            print(f"📊 Статус деплоя: {deployment['phase']}")
            
            # Причина обновления
            if 'cause' in deployment:
                print(f"🔄 Причина: {deployment['cause']}")
                
        print("\n" + "="*50)
        
        # Получить список деплоев
        deployments_response = requests.get(f'https://api.digitalocean.com/v2/apps/{APP_ID}/deployments', headers=headers)
        if deployments_response.status_code == 200:
            deployments = deployments_response.json()['deployments']
            print("📋 Последние 3 деплоя:")
            
            for i, deploy in enumerate(deployments[:3]):
                print(f"{i+1}. ID: {deploy['id']}")
                print(f"   Статус: {deploy['phase']}")
                print(f"   Создан: {deploy['created_at']}")
                if 'cause' in deploy:
                    print(f"   Причина: {deploy['cause']}")
                print()
                
    else:
        print(f"❌ Ошибка получения данных: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("="*50)
print("💡 Если деплой застрял, попробуйте:")
print("1. Проверить логи в Digital Ocean Dashboard")
print("2. Создать новый деплой вручную")
print("3. Проверить переменные окружения")