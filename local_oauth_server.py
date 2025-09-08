#!/usr/bin/env python3
"""
Локальный OAuth сервер для получения authorization code
"""

import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import webbrowser
import time

CREDENTIALS_FILE = 'credentials/client_secret.json'
auth_code = None

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        if self.path.startswith('/?'):
            # Парсим параметры
            query = self.path[2:]  # убираем /?
            params = urllib.parse.parse_qs(query)
            
            if 'code' in params:
                auth_code = params['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                success_html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>OAuth2 Success</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .success { color: green; font-size: 24px; margin-bottom: 20px; }
                        .code { background: #f5f5f5; padding: 10px; font-family: monospace; border: 1px solid #ddd; margin: 20px 0; }
                    </style>
                </head>
                <body>
                    <div class="success">✅ OAuth2 Authorization Successful!</div>
                    <p>Authorization code получен:</p>
                    <div class="code">{}</div>
                    <p>Можете закрыть это окно. Токен будет сохранен автоматически.</p>
                </body>
                </html>
                """.format(auth_code)
                
                self.wfile.write(success_html.encode('utf-8'))
                
                # Останавливаем сервер через секунду
                threading.Timer(1.0, lambda: self.server.shutdown()).start()
                
            elif 'error' in params:
                error = params['error'][0]
                self.send_response(400)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                error_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>OAuth2 Error</title>
                </head>
                <body>
                    <h1>❌ OAuth2 Error</h1>
                    <p>Error: {error}</p>
                </body>
                </html>
                """
                self.wfile.write(error_html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Отключаем логи сервера
        pass

def start_oauth_flow():
    print("🚀 ЛОКАЛЬНЫЙ OAuth2 СЕРВЕР")
    print("=" * 60)
    
    # Читаем credentials
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            config = json.load(f)
        client_id = config['installed']['client_id']
    except Exception as e:
        print(f"❌ Ошибка чтения credentials: {e}")
        return None
    
    # Запускаем локальный сервер
    server = HTTPServer(('localhost', 8080), OAuthHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    print(f"🌐 Локальный сервер запущен на: http://localhost:8080")
    print(f"🆔 Client ID: {client_id}")
    print()
    
    # Генерируем OAuth URL с localhost redirect
    redirect_uri = "http://localhost:8080"
    scope = "https://www.googleapis.com/auth/spreadsheets"
    
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'response_type': 'code',
        'access_type': 'offline',
        'include_granted_scopes': 'true'
    }
    
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    query_string = urllib.parse.urlencode(params)
    oauth_url = f"{base_url}?{query_string}"
    
    print("🔗 OAuth URL (будет открыт автоматически):")
    print("=" * 80)
    print(oauth_url)
    print("=" * 80)
    print()
    
    print("📋 Автоматическое открытие браузера через 3 секунды...")
    print("   1. Войдите как: aleynikov.artem@gmail.com")
    print("   2. Разрешите доступ к Google Sheets")
    print("   3. Код будет получен автоматически")
    print()
    
    # Ждем 3 секунды и открываем браузер
    time.sleep(3)
    try:
        webbrowser.open(oauth_url)
        print("🌐 Браузер открыт автоматически")
    except Exception as e:
        print(f"⚠️ Не удалось открыть браузер автоматически: {e}")
        print("📋 Скопируйте URL выше и откройте в браузере вручную")
    
    print("⏳ Ожидание authorization code...")
    
    # Ждем код до 5 минут
    timeout = 300  # 5 минут
    start_time = time.time()
    
    while auth_code is None and (time.time() - start_time) < timeout:
        time.sleep(1)
    
    server.shutdown()
    
    if auth_code:
        print(f"✅ Authorization code получен: {auth_code[:50]}...")
        return auth_code
    else:
        print("❌ Timeout: authorization code не получен")
        return None

if __name__ == "__main__":
    code = start_oauth_flow()
    if code:
        print()
        print("🎉 Успешно! Теперь сохраняем токен...")
        
        # Импортируем функцию сохранения
        try:
            from save_token import save_token
            success = save_token(code)
            
            if success:
                print("✅ Токен сохранен! Запускаем тест Google Sheets...")
                
                # Импортируем и запускаем тест
                from test_sheets import test_sheets
                test_success = test_sheets()
                
                if test_success:
                    print()
                    print("🚀 ИНТЕГРАЦИЯ GOOGLE SHEETS ГОТОВА!")
                    print("=" * 80)
                    print("✅ OAuth2 авторизация завершена")
                    print("✅ Google таблица создана")  
                    print("✅ Интеграция с ботом готова")
                else:
                    print("❌ Ошибка при создании Google таблицы")
            else:
                print("❌ Ошибка при сохранении токена")
                
        except ImportError as e:
            print(f"❌ Ошибка импорта: {e}")
            print("💡 Запустите: python save_token.py {code}")
    else:
        print("❌ OAuth2 авторизация не завершена")