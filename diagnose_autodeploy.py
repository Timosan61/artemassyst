#!/usr/bin/env python3
"""
🔍 Диагностика автоматического деплоя Digital Ocean
Проверяет почему не работает GitHub integration
"""

import requests
import json
from datetime import datetime

APP_ID = "86f72a9c-8404-4fc5-82c7-081931df3ba9"
GITHUB_REPO = "Timosan61/artemassyst"

print("🔍 Диагностика автоматического деплоя artemassyst...")
print(f"App ID: {APP_ID}")
print(f"GitHub: {GITHUB_REPO}")
print("="*60)

# 1. Проверяем последние коммиты в GitHub
print("\n1️⃣ ПОСЛЕДНИЕ КОММИТЫ В GITHUB:")
try:
    github_response = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}/commits", 
                                  params={"per_page": 5})
    if github_response.status_code == 200:
        commits = github_response.json()
        for i, commit in enumerate(commits):
            sha = commit['sha'][:8]
            message = commit['commit']['message'].split('\n')[0]
            date = commit['commit']['author']['date']
            print(f"  {i+1}. {sha} - {message}")
            print(f"     📅 {date}")
    else:
        print(f"❌ Ошибка получения коммитов: {github_response.status_code}")
except Exception as e:
    print(f"❌ Ошибка GitHub API: {e}")

# 2. Проверяем статус текущего приложения
print("\n2️⃣ СТАТУС ПРИЛОЖЕНИЯ DIGITAL OCEAN:")
print("(Необходим DIGITALOCEAN_TOKEN для полной диагностики)")

# 3. Проверяем настройки деплоя
print("\n3️⃣ ВОЗМОЖНЫЕ ПРИЧИНЫ ПРОБЛЕМ:")
print("🔸 GitHub integration отключен или поврежден")
print("🔸 Webhook не настроен в GitHub репозитории")
print("🔸 Digital Ocean не может получить доступ к репозиторию")
print("🔸 Превышен лимит деплоев или есть конфликты")
print("🔸 Ошибки в настройках автоматического деплоя")

# 4. Проверяем доступность репозитория
print("\n4️⃣ ДОСТУПНОСТЬ РЕПОЗИТОРИЯ:")
try:
    repo_response = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}")
    if repo_response.status_code == 200:
        repo_data = repo_response.json()
        print(f"✅ Репозиторий доступен: {repo_data['full_name']}")
        print(f"📊 Последний push: {repo_data['pushed_at']}")
        print(f"🌿 Ветка по умолчанию: {repo_data['default_branch']}")
        print(f"🔓 Публичный: {not repo_data['private']}")
    else:
        print(f"❌ Репозиторий недоступен: {repo_response.status_code}")
except Exception as e:
    print(f"❌ Ошибка проверки репозитория: {e}")

# 5. Проверяем webhook GitHub
print("\n5️⃣ WEBHOOKS В GITHUB РЕПОЗИТОРИИ:")
print("(Требует токен GitHub для полной проверки)")
print("Проверьте в GitHub: Settings → Webhooks")
print("Должен быть webhook для Digital Ocean App Platform")

# 6. Рекомендации по исправлению
print("\n6️⃣ РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ:")
print("1. Зайдите в Digital Ocean → Apps → artemassyst")
print("2. Перейдите в Settings → General")
print("3. Проверьте Source Code (GitHub integration)")
print("4. Если отключен - переподключите GitHub")
print("5. Убедитесь что выбран правильный репозиторий и ветка")
print("6. Проверьте Auto Deploy включен")

# 7. Тестовый коммит
print("\n7️⃣ ТЕСТИРОВАНИЕ АВТОДЕПЛОЯ:")
print("После исправления настроек:")
print("1. Сделайте тестовый коммит: git commit --allow-empty -m 'test autodeploy'")
print("2. git push origin main")
print("3. Проверьте появился ли новый деплой в Digital Ocean")

print("\n" + "="*60)
print("🎯 РЕЗУЛЬТАТ: Нужно проверить настройки GitHub integration в Digital Ocean")
print("="*60)