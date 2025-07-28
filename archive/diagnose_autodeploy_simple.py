#!/usr/bin/env python3
"""
🔍 Диагностика автоматического деплоя без токена
Анализирует возможные причины проблем с GitHub integration
"""

import requests
import json
from datetime import datetime, timezone

GITHUB_REPO = "Timosan61/artemassyst"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}"

print("🔍 Диагностика автоматического деплоя artemassyst...")
print("="*60)

def check_github_repo():
    """Проверить GitHub репозиторий"""
    print("\n1️⃣ ПРОВЕРКА GITHUB РЕПОЗИТОРИЯ:")
    try:
        # Информация о репозитории
        repo_response = requests.get(GITHUB_API)
        if repo_response.status_code == 200:
            repo_data = repo_response.json()
            print(f"✅ Репозиторий: {repo_data['full_name']}")
            print(f"📊 Последний push: {repo_data['pushed_at']}")
            print(f"🌿 Ветка по умолчанию: {repo_data['default_branch']}")
            print(f"🔓 Публичный: {not repo_data['private']}")
            print(f"⭐ Stars: {repo_data['stargazers_count']}")
            return repo_data
        else:
            print(f"❌ Репозиторий недоступен: {repo_response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def check_recent_commits():
    """Проверить последние коммиты"""
    print("\n2️⃣ ПОСЛЕДНИЕ КОММИТЫ:")
    try:
        commits_response = requests.get(f"{GITHUB_API}/commits", params={"per_page": 5})
        if commits_response.status_code == 200:
            commits = commits_response.json()
            for i, commit in enumerate(commits):
                sha = commit['sha'][:8]
                message = commit['commit']['message'].split('\n')[0]
                date = commit['commit']['author']['date']
                
                # Преобразуем дату в читаемый формат
                commit_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                time_ago = datetime.now(timezone.utc) - commit_date
                
                if time_ago.days > 0:
                    time_str = f"{time_ago.days} дней назад"
                elif time_ago.seconds > 3600:
                    time_str = f"{time_ago.seconds // 3600} часов назад"  
                else:
                    time_str = f"{time_ago.seconds // 60} минут назад"
                
                print(f"  {i+1}. {sha} - {message}")
                print(f"     📅 {date} ({time_str})")
            
            return commits
        else:
            print(f"❌ Ошибка получения коммитов: {commits_response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []

def check_webhooks():
    """Проверить webhooks (требует токен, но покажем что проверить)"""
    print("\n3️⃣ ПРОВЕРКА WEBHOOKS:")
    print("⚠️ Для полной проверки нужен GitHub токен")
    print("📋 Что нужно проверить в GitHub:")
    print("   • Settings → Webhooks")
    print("   • Должен быть webhook от Digital Ocean")
    print("   • URL должен содержать: hooks.digitalocean.com")
    print("   • Events: push, pull_request")
    print("   • Status: активный (зеленая галочка)")

def analyze_deployment_issues():
    """Анализ возможных проблем"""
    print("\n4️⃣ ВОЗМОЖНЫЕ ПРИЧИНЫ ПРОБЛЕМ:")
    
    issues = [
        "🔸 GitHub integration отключен в Digital Ocean",
        "🔸 Webhook не работает или удален",
        "🔸 Digital Ocean не имеет доступа к репозиторию",
        "🔸 Превышен лимит деплоев в месяц",
        "🔸 Конфликт с ручными деплоями",
        "🔸 Временные проблемы с GitHub API",
        "🔸 Неправильная ветка или путь в настройках"
    ]
    
    for issue in issues:
        print(f"   {issue}")

def check_do_server():
    """Проверить доступность сервера Digital Ocean"""
    print("\n5️⃣ ПРОВЕРКА СЕРВЕРА DIGITAL OCEAN:")
    try:
        response = requests.get("https://artemassyst-bot-tt5dt.ondigitalocean.app/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Сервер доступен")
            print(f"📊 Статус: {data.get('status', 'Unknown')}")
            print(f"🤖 AI статус: {data.get('ai_status', 'Unknown')}")
            
            # Проверяем время последнего обновления
            debug_info = data.get('debug_info', {})
            last_update = debug_info.get('last_update_time')
            if last_update:
                print(f"📅 Последнее сообщение боту: {last_update}")
            
            return True
        else:
            print(f"❌ Сервер вернул код: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Сервер недоступен: {e}")
        return False

def provide_solutions():
    """Предложить решения"""
    print("\n6️⃣ РЕШЕНИЯ ДЛЯ ВОССТАНОВЛЕНИЯ АВТОДЕПЛОЯ:")
    
    print("\n🔧 БЫСТРОЕ ИСПРАВЛЕНИЕ:")
    print("1. Digital Ocean Dashboard → Apps → artemassyst")
    print("2. Settings → General → Source Code")
    print("3. Нажать 'Edit' рядом с GitHub")
    print("4. Переподключить GitHub (Reconnect)")
    print("5. Выбрать репозиторий: Timosan61/artemassyst")
    print("6. Выбрать ветку: main")
    print("7. Включить 'Autodeploy: ON'")
    print("8. Save")
    
    print("\n🧪 ТЕСТИРОВАНИЕ:")
    print("После исправления проверить:")
    print("  git commit --allow-empty -m 'test: проверка автодеплоя'")
    print("  git push origin main")
    print("  # Через 2-3 минуты должен появиться новый деплой")
    
    print("\n📋 АЛЬТЕРНАТИВНЫЕ РЕШЕНИЯ:")
    print("• Если не помогает - удалить и заново создать GitHub подключение")
    print("• Проверить права доступа GitHub App 'DigitalOcean App Platform'")
    print("• Связаться с поддержкой Digital Ocean")
    
    print("\n⚡ ВРЕМЕННОЕ РЕШЕНИЕ:")
    print("• Использовать ручной деплой при каждом изменении")
    print("• Настроить GitHub Actions для автоматизации")

def main():
    print(f"🔗 GitHub Repo: {GITHUB_REPO}")
    print(f"🌐 Digital Ocean App: artemassyst-bot-tt5dt.ondigitalocean.app")
    
    # Проверяемся все компоненты
    repo_data = check_github_repo()
    commits = check_recent_commits()
    check_webhooks()
    analyze_deployment_issues()
    server_ok = check_do_server()
    provide_solutions()
    
    print("\n" + "="*60)
    print("📊 ИТОГОВАЯ ДИАГНОСТИКА:")
    
    if repo_data and commits and server_ok:
        print("✅ GitHub репозиторий работает нормально")
        print("✅ Коммиты поступают регулярно")
        print("✅ Digital Ocean сервер доступен")
        print("❌ Проблема скорее всего в GitHub integration")
        print("🔧 ДЕЙСТВИЕ: Переподключить GitHub в Digital Ocean")
    else:
        print("❌ Обнаружены проблемы с компонентами")
        print("🔧 ДЕЙСТВИЕ: Сначала исправить базовые проблемы")
    
    print("="*60)

if __name__ == "__main__":
    main()