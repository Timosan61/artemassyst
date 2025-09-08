#!/bin/bash

# Railway Deploy Script
# Деплой бота на Railway через GitHub интеграцию

echo "🚀 Начинаем деплой на Railway"
echo "================================"

# Проверяем что все изменения в GitHub
git_status=$(git status --porcelain)
if [ ! -z "$git_status" ]; then
    echo "⚠️  Есть незакоммиченные изменения. Коммитим..."
    git add -A
    git commit -m "Auto-deploy: обновление бота для недвижимости"
    git push origin main
else
    echo "✅ Все изменения уже в GitHub"
fi

echo ""
echo "📦 Railway автоматически деплоит из GitHub"
echo "==========================================="
echo ""
echo "Railway настроен на автоматический деплой при каждом push в main ветку."
echo ""
echo "🔗 Ссылки:"
echo "- Проект Railway: https://railway.app/project/6a08cc81-8944-4807-ab6f-79b06a7840df"
echo "- GitHub репозиторий: https://github.com/Timosan61/artemassyst"
echo ""
echo "📊 Что происходит сейчас:"
echo "1. ✅ Код отправлен на GitHub"
echo "2. 🔄 Railway автоматически получает изменения"
echo "3. 🏗️ Railway собирает Docker образ"
echo "4. 🚀 Railway деплоит новую версию"
echo ""
echo "⏱️ Процесс занимает 3-5 минут"
echo ""
echo "📱 Проверьте бота в Telegram: @artem_integrator_bot"
echo ""
echo "💡 Для просмотра логов используйте:"
echo "   railway logs --follow"
echo ""
echo "✅ Деплой запущен!"