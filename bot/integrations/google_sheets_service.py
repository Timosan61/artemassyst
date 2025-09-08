"""
Google Sheets интеграционный сервис для бота Алена
Синхронизация данных из ZEP Cloud с Google Таблицами
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .sheets_config import (
    SCOPES, CREDENTIALS_FILE, TOKEN_FILE, SPREADSHEET_NAME,
    SHEET_CONFIGURATIONS, DEFAULT_SYNC_INTERVAL, BATCH_SIZE,
    TARGET_EMAIL
)
from ..memory.memory_service import MemoryService
from ..memory.analytics import AnalyticsService

logger = logging.getLogger(__name__)


class GoogleSheetsService:
    """Сервис для интеграции с Google Sheets и синхронизации данных из ZEP Cloud"""
    
    def __init__(self, memory_service: MemoryService, analytics_service: AnalyticsService):
        self.memory_service = memory_service
        self.analytics_service = analytics_service
        self.service = None
        self.spreadsheet_id = None
        self._authenticated = False
    
    async def authenticate(self) -> bool:
        """Аутентификация через OAuth2 и инициализация Google Sheets API"""
        try:
            creds = None
            
            # Проверяем существующие токены
            if os.path.exists(TOKEN_FILE):
                creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            
            # Если нет валидных учетных данных, запускаем OAuth флоу
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    # Обновляем токен
                    await asyncio.to_thread(creds.refresh, Request())
                    logger.info("🔄 Google Sheets токен обновлен")
                else:
                    # Запускаем новый OAuth флоу
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_FILE, SCOPES)
                    creds = await asyncio.to_thread(flow.run_local_server, port=0)
                    logger.info("✅ Новый Google Sheets токен получен")
                
                # Сохраняем токен для последующего использования
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
            
            # Инициализируем сервис Google Sheets API
            self.service = await asyncio.to_thread(
                build, 'sheets', 'v4', credentials=creds
            )
            self._authenticated = True
            logger.info("🎯 Google Sheets API успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка аутентификации Google Sheets: {e}")
            self._authenticated = False
            return False
    
    async def create_spreadsheet(self) -> Optional[str]:
        """Создает новую Google таблицу с необходимой структурой листов"""
        if not self._authenticated:
            if not await self.authenticate():
                return None
        
        try:
            # Создаем основную таблицу
            spreadsheet = {
                'properties': {
                    'title': SPREADSHEET_NAME,
                    'locale': 'ru_RU',
                    'timeZone': 'Europe/Moscow'
                },
                'sheets': []
            }
            
            # Добавляем листы согласно конфигурации
            for sheet_key, sheet_config in SHEET_CONFIGURATIONS.items():
                sheet = {
                    'properties': {
                        'title': sheet_config['name'],
                        'gridProperties': {
                            'rowCount': 1000,
                            'columnCount': len(sheet_config['headers'])
                        }
                    }
                }
                spreadsheet['sheets'].append(sheet)
            
            # Создаем таблицу
            result = await asyncio.to_thread(
                self.service.spreadsheets().create,
                body=spreadsheet
            )
            
            response = await asyncio.to_thread(result.execute)
            self.spreadsheet_id = response['spreadsheetId']
            
            logger.info(f"📊 Создана Google таблица: {self.spreadsheet_id}")
            
            # Настраиваем заголовки для каждого листа
            await self._setup_sheet_headers()
            
            # Предоставляем доступ целевому email
            await self._share_spreadsheet()
            
            logger.info(f"✅ Google таблица готова: https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}")
            return self.spreadsheet_id
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания Google таблицы: {e}")
            return None
    
    async def _setup_sheet_headers(self):
        """Настраивает заголовки для всех листов таблицы"""
        if not self.spreadsheet_id:
            return
        
        try:
            requests = []
            
            for sheet_key, sheet_config in SHEET_CONFIGURATIONS.items():
                # Получаем ID листа
                sheet_metadata = await asyncio.to_thread(
                    self.service.spreadsheets().get,
                    spreadsheetId=self.spreadsheet_id
                )
                
                sheets_info = await asyncio.to_thread(sheet_metadata.execute)
                sheet_id = None
                
                for sheet in sheets_info['sheets']:
                    if sheet['properties']['title'] == sheet_config['name']:
                        sheet_id = sheet['properties']['sheetId']
                        break
                
                if sheet_id is None:
                    continue
                
                # Добавляем заголовки
                header_values = [[header for header in sheet_config['headers']]]
                
                requests.append({
                    'updateCells': {
                        'range': {
                            'sheetId': sheet_id,
                            'startRowIndex': 0,
                            'endRowIndex': 1,
                            'startColumnIndex': 0,
                            'endColumnIndex': len(sheet_config['headers'])
                        },
                        'rows': [{
                            'values': [{
                                'userEnteredValue': {'stringValue': header},
                                'userEnteredFormat': {
                                    'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9},
                                    'textFormat': {'bold': True}
                                }
                            } for header in sheet_config['headers']]
                        }],
                        'fields': 'userEnteredValue,userEnteredFormat'
                    }
                })
            
            # Выполняем все запросы батчем
            if requests:
                batch_request = {'requests': requests}
                batch_update = await asyncio.to_thread(
                    self.service.spreadsheets().batchUpdate,
                    spreadsheetId=self.spreadsheet_id,
                    body=batch_request
                )
                await asyncio.to_thread(batch_update.execute)
                logger.info("📋 Заголовки листов настроены")
                
        except Exception as e:
            logger.error(f"❌ Ошибка настройки заголовков: {e}")
    
    async def _share_spreadsheet(self):
        """Предоставляет доступ к таблице указанному email"""
        if not self.spreadsheet_id:
            return
        
        try:
            # Создаем сервис Drive API для управления доступом
            drive_service = await asyncio.to_thread(
                build, 'drive', 'v3', credentials=self.service._http.credentials
            )
            
            # Предоставляем доступ
            permission = {
                'type': 'user',
                'role': 'writer',
                'emailAddress': TARGET_EMAIL
            }
            
            permission_request = await asyncio.to_thread(
                drive_service.permissions().create,
                fileId=self.spreadsheet_id,
                body=permission,
                sendNotificationEmail=True
            )
            
            await asyncio.to_thread(permission_request.execute)
            logger.info(f"✅ Доступ к таблице предоставлен: {TARGET_EMAIL}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка предоставления доступа: {e}")
    
    async def sync_leads_data(self, days: int = 30) -> bool:
        """Синхронизирует данные лидов из ZEP Cloud в Google Sheets"""
        if not self._authenticated or not self.spreadsheet_id:
            logger.error("❌ Google Sheets не инициализирован")
            return False
        
        try:
            # Получаем данные из ZEP Cloud через memory_service
            # Пока используем заглушку - в реальности нужно получать из ZEP
            leads_data = await self._get_leads_from_zep(days)
            
            if not leads_data:
                logger.info("📭 Нет данных лидов для синхронизации")
                return True
            
            # Подготавливаем данные для Google Sheets
            sheet_values = []
            for lead in leads_data:
                row = self._convert_lead_to_row(lead)
                sheet_values.append(row)
            
            # Обновляем лист клиентов
            range_name = f"{SHEET_CONFIGURATIONS['clients']['name']}!A2:AG"
            
            # Очищаем существующие данные (кроме заголовков)
            clear_request = await asyncio.to_thread(
                self.service.spreadsheets().values().clear,
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            )
            await asyncio.to_thread(clear_request.execute)
            
            # Добавляем новые данные
            if sheet_values:
                body = {
                    'values': sheet_values
                }
                
                update_request = await asyncio.to_thread(
                    self.service.spreadsheets().values().update,
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption='RAW',
                    body=body
                )
                
                await asyncio.to_thread(update_request.execute)
                logger.info(f"📊 Синхронизировано {len(sheet_values)} лидов")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка синхронизации лидов: {e}")
            return False
    
    async def sync_analytics_data(self, days: int = 30) -> bool:
        """Синхронизирует аналитические данные из ZEP Cloud"""
        if not self._authenticated or not self.spreadsheet_id:
            return False
        
        try:
            # Синхронизируем события
            await self._sync_events_data(days)
            
            # Синхронизируем воронку конверсии
            await self._sync_funnel_data(days)
            
            # Синхронизируем ежедневную статистику
            await self._sync_daily_stats(days)
            
            logger.info(f"📈 Аналитические данные синхронизированы за {days} дней")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка синхронизации аналитики: {e}")
            return False
    
    async def _sync_events_data(self, days: int):
        """Синхронизирует события в лист 'Аналитика событий'"""
        try:
            # Получаем недавние события из аналитики
            recent_events = await self.analytics_service._get_recent_events(hours=days*24)
            
            if not recent_events:
                return
            
            # Подготавливаем данные для листа событий
            sheet_values = []
            for event in recent_events:
                row = [
                    event.get('session_id', ''),
                    event.get('event_type', ''),
                    str(event.get('event_data', {})),
                    event.get('timestamp', '')
                ]
                sheet_values.append(row)
            
            # Обновляем лист
            range_name = f"{SHEET_CONFIGURATIONS['events']['name']}!A2:D"
            await self._update_sheet_range(range_name, sheet_values)
            
        except Exception as e:
            logger.error(f"❌ Ошибка синхронизации событий: {e}")
    
    async def _sync_funnel_data(self, days: int):
        """Синхронизирует данные воронки конверсии"""
        try:
            # Получаем данные воронки
            funnel_data = await self.analytics_service.get_conversion_funnel(days)
            
            if not funnel_data:
                return
            
            # Подготавливаем данные
            sheet_values = []
            funnel_stats = funnel_data.get('funnel_data', {})
            conversion_rates = funnel_data.get('conversion_rates', {})
            
            for state, count in funnel_stats.items():
                conversion_rate = conversion_rates.get(state, 0.0)
                row = [
                    state,
                    count,
                    f"{conversion_rate:.2f}%",
                    datetime.now().strftime('%Y-%m-%d')
                ]
                sheet_values.append(row)
            
            # Обновляем лист
            range_name = f"{SHEET_CONFIGURATIONS['funnel']['name']}!A2:D"
            await self._update_sheet_range(range_name, sheet_values)
            
        except Exception as e:
            logger.error(f"❌ Ошибка синхронизации воронки: {e}")
    
    async def _sync_daily_stats(self, days: int):
        """Синхронизирует ежедневную статистику"""
        try:
            # Получаем ежедневную статистику
            daily_stats = await self.analytics_service.get_daily_stats(days)
            
            if not daily_stats:
                return
            
            # Подготавливаем данные
            sheet_values = []
            for day_data in daily_stats:
                event_types = day_data.get('event_types', {})
                new_leads = event_types.get('new_lead', 0)
                hot_leads = event_types.get('qualification_hot', 0)
                escalations = event_types.get('escalation', 0)
                
                row = [
                    day_data.get('date', ''),
                    day_data.get('total_events', 0),
                    day_data.get('unique_sessions', 0),
                    new_leads,
                    hot_leads,
                    escalations
                ]
                sheet_values.append(row)
            
            # Обновляем лист
            range_name = f"{SHEET_CONFIGURATIONS['daily_stats']['name']}!A2:F"
            await self._update_sheet_range(range_name, sheet_values)
            
        except Exception as e:
            logger.error(f"❌ Ошибка синхронизации ежедневной статистики: {e}")
    
    async def _update_sheet_range(self, range_name: str, values: List[List]):
        """Обновляет указанный диапазон листа"""
        try:
            # Очищаем диапазон
            clear_request = await asyncio.to_thread(
                self.service.spreadsheets().values().clear,
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            )
            await asyncio.to_thread(clear_request.execute)
            
            # Добавляем новые данные
            if values:
                body = {'values': values}
                update_request = await asyncio.to_thread(
                    self.service.spreadsheets().values().update,
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption='RAW',
                    body=body
                )
                await asyncio.to_thread(update_request.execute)
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления диапазона {range_name}: {e}")
    
    async def _get_leads_from_zep(self, days: int) -> List[Dict[str, Any]]:
        """Получает данные лидов из ZEP Cloud через MemoryService"""
        try:
            # Пока заглушка - нужно реализовать получение данных из ZEP
            # В реальности здесь будет вызов memory_service для получения всех сессий
            # и их данных за указанный период
            
            leads = []
            # Пример структуры данных лида
            sample_lead = {
                'session_id': 'example_session',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'name': '',
                'phone': '',
                'telegram_username': '',
                'whatsapp': '',
                'city': '',
                'in_sochi_now': '',
                'arrival_date': '',
                'local_resident': '',
                'purchase_goal': '',
                'payment_type': '',
                'bank': '',
                'need_to_sell': '',
                'budget_min': '',
                'budget_max': '',
                'locations': '',
                'property_type': '',
                'parameters': '',
                'experience_in_sochi': '',
                'urgency': '',
                'remote_deal': '',
                'online_showing_readiness': '',
                'preferred_slots': '',
                'communication_channel': '',
                'qualification': '',
                'next_action': '',
                'assigned_manager': '',
                'utm_source': '',
                'comments': '',
                'dialog_state': ''
            }
            
            return leads
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения лидов из ZEP: {e}")
            return []
    
    def _convert_lead_to_row(self, lead_data: Dict[str, Any]) -> List[str]:
        """Конвертирует данные лида в строку для Google Sheets"""
        headers = SHEET_CONFIGURATIONS['clients']['headers']
        row = []
        
        # Маппинг полей в соответствии с заголовками
        field_mapping = {
            'ID сессии': 'session_id',
            'Дата создания': 'created_at',
            'Дата обновления': 'updated_at',
            'Имя': 'name',
            'Телефон': 'phone',
            'Telegram Username': 'telegram_username',
            'WhatsApp': 'whatsapp',
            'Город клиента': 'city',
            'Находится в Сочи сейчас': 'in_sochi_now',
            'Дата прилёта': 'arrival_date',
            'Местный житель': 'local_resident',
            'Цель покупки': 'purchase_goal',
            'Форма оплаты': 'payment_type',
            'Банк': 'bank',
            'Нужно продать своё': 'need_to_sell',
            'Бюджет мин': 'budget_min',
            'Бюджет макс': 'budget_max',
            'Локации': 'locations',
            'Тип объекта': 'property_type',
            'Параметры': 'parameters',
            'Опыт в Сочи': 'experience_in_sochi',
            'Срочность': 'urgency',
            'Удалённая сделка': 'remote_deal',
            'Готовность к онлайн-показу': 'online_showing_readiness',
            'Предпочтительные слоты': 'preferred_slots',
            'Канал связи': 'communication_channel',
            'Квалификация': 'qualification',
            'Следующее действие': 'next_action',
            'Назначенный менеджер': 'assigned_manager',
            'UTM источник': 'utm_source',
            'Комментарии': 'comments',
            'Состояние диалога': 'dialog_state'
        }
        
        for header in headers:
            field_key = field_mapping.get(header, '')
            value = lead_data.get(field_key, '')
            row.append(str(value) if value else '')
        
        return row
    
    async def setup_periodic_sync(self, interval_seconds: int = DEFAULT_SYNC_INTERVAL):
        """Настраивает периодическую синхронизацию данных"""
        logger.info(f"🔄 Настройка периодической синхронизации каждые {interval_seconds} секунд")
        
        while True:
            try:
                await asyncio.sleep(interval_seconds)
                
                if self._authenticated and self.spreadsheet_id:
                    logger.info("🔄 Запуск периодической синхронизации")
                    
                    # Синхронизируем лиды
                    await self.sync_leads_data()
                    
                    # Синхронизируем аналитику
                    await self.sync_analytics_data()
                    
                    logger.info("✅ Периодическая синхронизация завершена")
                else:
                    logger.warning("⚠️ Google Sheets не готов для синхронизации")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка в периодической синхронизации: {e}")
                await asyncio.sleep(60)  # Пауза перед повтором при ошибке
    
    async def get_spreadsheet_url(self) -> Optional[str]:
        """Возвращает URL созданной Google таблицы"""
        if self.spreadsheet_id:
            return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}"
        return None
    
    async def health_check(self) -> bool:
        """Проверка состояния сервиса"""
        return self._authenticated and self.spreadsheet_id is not None