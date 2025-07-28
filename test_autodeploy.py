#!/usr/bin/env python3
"""
🧪 Тестирование автоматического деплоя
Создает тестовый коммит и проверяет появление деплоя
"""

import subprocess
import requests
import time
from datetime import datetime

GITHUB_REPO = "Timosan61/artemassyst"

def create_test_commit():
    """Создать тестовый коммит для проверки автодеплоя"""
    print("🧪 СОЗДАНИЕ ТЕСТОВОГО КОММИТА:")
    
    try:
        # Создаем empty commit с временной меткой
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"test: проверка автодеплоя {timestamp}"
        
        # Выполняем git команды
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "--allow-empty", "-m", commit_message], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print(f"✅ Тестовый коммит создан: {commit_message}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка создания коммита: {e}")
        return False

def check_latest_commit():
    """Получить SHA последнего коммита"""
    try:
        response = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}/commits", 
                               params={"per_page": 1})
        if response.status_code == 200:
            commits = response.json()
            if commits:
                return commits[0]['sha']
        return None
    except:
        return None

def monitor_for_deployment(initial_sha, timeout_minutes=10):
    """Мониторить появление нового деплоя"""
    print(f"\n⏳ МОНИТОРИНГ АВТОДЕПЛОЯ (макс. {timeout_minutes} мин):")
    print(f"🔍 Ожидаем деплой для коммита: {initial_sha[:8]}...")
    
    # Проверяем есть ли webhook в GitHub
    print("\n📋 ПРОВЕРЬТЕ WEBHOOK В GITHUB:")
    print("1. Откройте https://github.com/Timosan61/artemassyst/settings/hooks")
    print("2. Найдите webhook для Digital Ocean App Platform")
    print("3. Проверьте что он активен (зеленая галочка)")
    print("4. URL должен содержать: hooks.digitalocean.com")
    
    # Проверяем Digital Ocean приложение
    print("\n📋 ПРОВЕРЬТЕ DIGITAL OCEAN:")
    print("1. Откройте https://cloud.digitalocean.com/apps")
    print("2. Выберите artemassyst")
    print("3. Во вкладке 'Activity' должен появиться новый деплой")
    print("4. Статус должен измениться на 'Building...'")
    
    # Мониторим изменения коммитов
    for minute in range(timeout_minutes):
        time.sleep(60)  # Ждем 1 минуту
        
        current_sha = check_latest_commit()
        if current_sha and current_sha != initial_sha:
            print(f"✅ [{minute+1} мин] Новый коммит обнаружен: {current_sha[:8]}")
        
        print(f"⏰ [{minute+1}/{timeout_minutes} мин] Мониторим...")
        
        # Проверяем доступность сервера
        try:
            response = requests.get("https://artemassyst-bot-tt5dt.ondigitalocean.app/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                last_update = data.get('debug_info', {}).get('version_info', {}).get('last_commit_sha', '')
                if last_update.startswith(initial_sha[:8]):
                    print(f"🎉 АВТОДЕПЛОЙ РАБОТАЕТ! Сервер обновлен с коммитом {initial_sha[:8]}")
                    return True
        except:
            pass
    
    print(f"⏰ Время ожидания {timeout_minutes} минут истекло")
    return False

def main():
    print("🧪 ТЕСТИРОВАНИЕ АВТОМАТИЧЕСКОГО ДЕПЛОЯ")
    print("="*50)
    
    # Получаем текущий SHA
    initial_sha = check_latest_commit()
    if not initial_sha:
        print("❌ Не удалось получить информацию о коммитах")
        return
    
    print(f"📊 Текущий коммит: {initial_sha[:8]}")
    
    # Создаем тестовый коммит
    if not create_test_commit():
        return
    
    # Получаем новый SHA
    new_sha = check_latest_commit()
    if not new_sha or new_sha == initial_sha:
        print("❌ Тестовый коммит не появился в GitHub")
        return
    
    print(f"📊 Новый коммит: {new_sha[:8]}")
    
    # Мониторим автодеплой
    success = monitor_for_deployment(new_sha)
    
    print("\n" + "="*50)
    if success:
        print("✅ АВТОДЕПЛОЙ РАБОТАЕТ ИСПРАВНО!")
    else:
        print("❌ АВТОДЕПЛОЙ НЕ СРАБОТАЛ")
        print("🔧 Проверьте GitHub integration в Digital Ocean")
    print("="*50)

if __name__ == "__main__":
    main()