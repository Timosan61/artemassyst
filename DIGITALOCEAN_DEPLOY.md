# 🐙 Деплой artemmyassyst на Digital Ocean App Platform

Полное руководство по развертыванию artemmyassyst бота на Digital Ocean App Platform.

## 📋 Предварительные требования

### 1. Создание бота в Telegram
1. Перейдите к [@BotFather](https://t.me/BotFather) в Telegram
2. Создайте нового бота: `/newbot`
3. Имя: `artemmyassyst` 
4. Username: `artemmyassyst_bot`
5. Сохраните полученный токен

### 2. Подготовка GitHub репозитория
1. Создайте новый репозиторий на GitHub: `artemmyassyst`
2. Загрузите код бота в репозиторий
3. Убедитесь что файлы `app.yaml` и `Dockerfile.digitalocean` присутствуют

## 🚀 Деплой на Digital Ocean

### Шаг 1: Создание приложения
1. Войдите в [Digital Ocean App Platform](https://cloud.digitalocean.com/apps)
2. Нажмите **"Create App"**
3. Выберите **"GitHub"** как источник кода
4. Подключите ваш GitHub аккаунт
5. Выберите репозиторий `artemmyassyst`
6. Ветка: `main`

### Шаг 2: Конфигурация приложения
1. **App Info:**
   - Name: `artemmyassyst-app`
   - Region: `New York (NYC1)` или ближайший к вам

2. **Service Configuration:**
   - Service Type: `Web Service`
   - Source Directory: `/`
   - Build Command: (автоматически)
   - Run Command: `python webhook.py`
   - Port: `8000`

### Шаг 3: Переменные окружения
Добавьте следующие environment variables:

#### Обязательные переменные:
```
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_FROM_BOTFATHER
BOT_USERNAME=artemmyassyst_bot
WEBHOOK_SECRET_TOKEN=artemmyassyst_secret_2025_randomhex
WEBHOOK_URL=https://artemmyassyst-app.ondigitalocean.app/webhook
```

#### AI ключи (из artem.integrator):
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ZEP_API_KEY=your_zep_api_key_here
```

#### Системные переменные:
```
PORT=8000
PYTHONPATH=/app
ADMIN_PASSWORD=artemmyassyst_admin_2025
```

### Шаг 4: Завершение создания
1. Нажмите **"Next"** 
2. Проверьте конфигурацию
3. Нажмите **"Create Resources"**
4. Дождитесь завершения деплоя (5-10 минут)

## 🔧 Настройка после деплоя

### 1. Получение URL приложения
После успешного деплоя вы получите URL:
```
https://artemmyassyst-app-randomid.ondigitalocean.app
```

### 2. Обновление переменных окружения
1. В Digital Ocean Dashboard перейдите в **Settings** → **Environment Variables**
2. Обновите `WEBHOOK_URL` на реальный URL:
```
WEBHOOK_URL=https://your-actual-app-url.ondigitalocean.app/webhook
```

### 3. Проверка работы бота
1. **Health check:** `https://your-app-url.ondigitalocean.app/`
2. **Установка webhook:** `https://your-app-url.ondigitalocean.app/webhook/set`
3. **Админ панель:** `https://your-app-url.ondigitalocean.app/admin` (если настроена)

## 📊 Мониторинг и отладка

### Digital Ocean Dashboard
- **Logs:** Runtime Logs для просмотра логов приложения
- **Metrics:** CPU, Memory, Response Time
- **Settings:** Environment Variables, Scaling

### Debug endpoints
- `/` - Статус приложения
- `/webhook/info` - Информация о webhook
- `/debug/last-updates` - Последние обновления от Telegram
- `/debug/logs` - Последние логи бота

### Типичные проблемы

#### 1. "Build failed"
- Проверьте `requirements.txt`
- Убедитесь что все зависимости указаны корректно

#### 2. "Application crashed"
- Проверьте переменные окружения
- Убедитесь что `TELEGRAM_BOT_TOKEN` корректный

#### 3. "Webhook не работает"
- Проверьте `WEBHOOK_URL` в переменных окружения
- Выполните `/webhook/set` для переустановки

## 💰 Стоимость

### Basic Plan (рекомендуется для начала):
- **Basic XXS:** $5/месяц
- 512MB RAM, 1 vCPU
- Достаточно для небольших/средних ботов

### Scaling:
- **Basic XS:** $12/месяц (1GB RAM)
- **Basic S:** $25/месяц (2GB RAM)

## 🔄 Обновления

### Автоматические обновления:
1. Внесите изменения в GitHub репозиторий
2. Push в ветку `main`
3. Digital Ocean автоматически пересоберет и задеплоит

### Ручное обновление:
1. В Digital Ocean Dashboard → Apps
2. Выберите ваше приложение
3. Actions → **"Force Rebuild and Deploy"**

## 🔐 Безопасность

### Рекомендации:
1. **Используйте Secrets** для всех API ключей
2. **Мониторьте логи** на предмет подозрительной активности
3. **Регулярно обновляйте** зависимости
4. **Ограничьте доступ** к админ панели

### Environment Variables как Secrets:
- `TELEGRAM_BOT_TOKEN` → Secret
- `ANTHROPIC_API_KEY` → Secret  
- `ZEP_API_KEY` → Secret
- `WEBHOOK_SECRET_TOKEN` → Secret
- `ADMIN_PASSWORD` → Secret

## 📞 Поддержка

### Документация:
- [Digital Ocean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

### Контакты:
- Создайте issue в GitHub репозитории
- Документация по боту: `README.md`