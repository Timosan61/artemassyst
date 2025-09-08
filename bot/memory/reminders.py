"""
Сервис напоминаний для системы памяти
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

from .models import ReminderTask

logger = logging.getLogger(__name__)


class ReminderService:
    """Сервис для управления напоминаниями и follow-up сообщениями"""
    
    def __init__(self, storage_path: str = "data/reminders"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Файл для хранения напоминаний
        self.reminders_file = self.storage_path / "reminders.json"
        
        # Шаблоны сообщений для напоминаний
        self.message_templates = {
            'follow_up_1h': [
                "{name}, актуально? Могу прислать 2–3 лучших объекта под ваш запрос.",
                "Есть время посмотреть варианты недвижимости в Сочи?",
                "{name}, подготовила несколько объектов. Актуально сейчас?"
            ],
            'follow_up_6h': [
                "Подошли свободные окна на онлайн-показ: 18:00 сегодня или 11:00 завтра.",
                "{name}, появился объект со скидкой в вашей вилке. Предложить?",
                "Есть интересный объект у моря в вашем бюджете. Посмотрим?"
            ],
            'follow_up_12h': [
                "Появился проект ниже рынка в вашем бюджете. Предложить?",
                "{name}, если не актуально — напишите, чтобы не отвлекать. Я на связи, когда потребуется.",
                "Завтра последний день скидки на объекты у моря. Интересно?"
            ],
            'follow_up_72h': [
                "Если не актуально — напишите, чтобы не отвлекать. Я на связи, когда потребуется.",
                "{name}, завершаю работу с вашим запросом. Если понадобится помощь — всегда рада!",
                "Если ситуация изменится и понадобится недвижимость — обращайтесь!"
            ],
            'demo_reminder': [
                "{name}, напоминаю о демо-показе сегодня в {time}. Ссылка: {demo_link}",
                "Через час демо-показ! Все готово, ждем вас: {demo_link}",
                "{name}, сегодня в {time} демо-показ. Подтверждаете участие?"
            ],
            'hot_lead_urgent': [
                "Есть срочная продажа ниже рынка — только до вечера. Интересно?",
                "Последний слот на сегодня: 19:00. Бронировать?",
                "Специальное предложение именно для вашей сферы. 5 минут на звонок?"
            ]
        }
    
    async def schedule_follow_up_sequence(self, session_id: str, 
                                        lead_data: Optional[Dict[str, Any]] = None):
        """Планирует последовательность напоминаний (1ч > 6ч > 12ч > 72ч)"""
        try:
            now = datetime.now()
            
            # Последовательность напоминаний
            follow_up_sequence = [
                (timedelta(hours=1), 'follow_up_1h'),
                (timedelta(hours=6), 'follow_up_6h'), 
                (timedelta(hours=12), 'follow_up_12h'),
                (timedelta(hours=72), 'follow_up_72h')
            ]
            
            reminders = []
            for i, (delay, template_type) in enumerate(follow_up_sequence):
                reminder = ReminderTask(
                    session_id=session_id,
                    reminder_type=f'follow_up_{i+1}',
                    scheduled_time=now + delay,
                    message_template=template_type,
                    attempt_number=i + 1,
                    max_attempts=4
                )
                reminders.append(reminder)
            
            # Сохраняем напоминания
            await self._save_reminders(reminders)
            
            logger.info(f"✅ Запланирована последовательность из {len(reminders)} напоминаний для {session_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка планирования напоминаний для {session_id}: {e}")
    
    async def schedule_demo_reminder(self, session_id: str, demo_time: datetime,
                                   lead_data: Optional[Dict[str, Any]] = None):
        """Планирует напоминание о демо"""
        try:
            # Напоминания за 1 час и за 10 минут до демо
            reminder_times = [
                demo_time - timedelta(hours=1),
                demo_time - timedelta(minutes=10)
            ]
            
            reminders = []
            for i, reminder_time in enumerate(reminder_times):
                if reminder_time > datetime.now():  # Только будущие напоминания
                    reminder = ReminderTask(
                        session_id=session_id,
                        reminder_type=f'demo_reminder_{i+1}',
                        scheduled_time=reminder_time,
                        message_template='demo_reminder',
                        attempt_number=1,
                        max_attempts=1
                    )
                    reminders.append(reminder)
            
            await self._save_reminders(reminders)
            
            logger.info(f"✅ Запланированы напоминания о демо для {session_id}: {len(reminders)} шт.")
            
        except Exception as e:
            logger.error(f"❌ Ошибка планирования напоминаний о демо для {session_id}: {e}")
    
    async def schedule_urgent_follow_up(self, session_id: str, 
                                      urgency_type: str = 'hot_lead_urgent'):
        """Планирует срочное напоминание для горячих лидов"""
        try:
            # Срочные напоминания через 30 минут и 2 часа
            urgent_times = [
                datetime.now() + timedelta(minutes=30),
                datetime.now() + timedelta(hours=2)
            ]
            
            reminders = []
            for i, reminder_time in enumerate(urgent_times):
                reminder = ReminderTask(
                    session_id=session_id,
                    reminder_type=f'{urgency_type}_{i+1}',
                    scheduled_time=reminder_time,
                    message_template=urgency_type,
                    attempt_number=1,
                    max_attempts=2
                )
                reminders.append(reminder)
            
            await self._save_reminders(reminders)
            
            logger.info(f"✅ Запланированы срочные напоминания для {session_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка планирования срочных напоминаний для {session_id}: {e}")
    
    async def get_due_reminders(self) -> List[ReminderTask]:
        """Получает напоминания, которые нужно отправить сейчас"""
        try:
            all_reminders = await self._load_reminders()
            due_reminders = []
            now = datetime.now()
            
            for reminder in all_reminders:
                if (not reminder.is_completed and 
                    reminder.scheduled_time <= now and 
                    reminder.attempt_number <= reminder.max_attempts):
                    due_reminders.append(reminder)
            
            return due_reminders
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения готовых напоминаний: {e}")
            return []
    
    async def generate_reminder_message(self, reminder: ReminderTask, 
                                      lead_data: Optional[Dict[str, Any]] = None) -> str:
        """Генерирует текст напоминания"""
        try:
            template_type = reminder.message_template
            templates = self.message_templates.get(template_type, [
                "Напоминание о вашем запросе на недвижимость. Актуально?"
            ])
            
            # Выбираем шаблон (можно по алгоритму или случайно)
            import random
            template = random.choice(templates)
            
            # Подставляем данные лида если есть
            if lead_data:
                message = template.format(
                    name=lead_data.get('name', ''),
                    business=lead_data.get('business_sphere', 'бизнеса'),
                    business_sphere=lead_data.get('business_sphere', 'вашей сферы'),
                    time='15:30',  # Можно динамически
                    demo_link='https://meet.google.com/demo-link'  # Можно динамически
                )
            else:
                # Базовое сообщение без персонализации
                message = template.replace('{name}', '').replace('{business}', 'бизнеса')
            
            return message.strip()
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации сообщения напоминания: {e}")
            return "Напоминание о вашем запросе на недвижимость. Актуально?"
    
    async def mark_reminder_completed(self, reminder: ReminderTask):
        """Помечает напоминание как выполненное"""
        try:
            all_reminders = await self._load_reminders()
            
            # Находим и обновляем напоминание
            for i, saved_reminder in enumerate(all_reminders):
                if (saved_reminder.session_id == reminder.session_id and
                    saved_reminder.reminder_type == reminder.reminder_type and
                    saved_reminder.scheduled_time == reminder.scheduled_time):
                    all_reminders[i].is_completed = True
                    break
            
            # Сохраняем обновленный список
            await self._save_all_reminders(all_reminders)
            
            logger.debug(f"✅ Напоминание помечено как выполненное: {reminder.reminder_type}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка отметки напоминания как выполненного: {e}")
    
    async def cancel_reminders(self, session_id: str, reminder_types: Optional[List[str]] = None):
        """Отменяет напоминания для сессии"""
        try:
            all_reminders = await self._load_reminders()
            
            # Фильтруем напоминания
            filtered_reminders = []
            cancelled_count = 0
            
            for reminder in all_reminders:
                should_cancel = (
                    reminder.session_id == session_id and
                    not reminder.is_completed and
                    (reminder_types is None or reminder.reminder_type in reminder_types)
                )
                
                if should_cancel:
                    reminder.is_completed = True  # Помечаем как выполненное = отмененное
                    cancelled_count += 1
                
                filtered_reminders.append(reminder)
            
            # Сохраняем обновленный список
            await self._save_all_reminders(filtered_reminders)
            
            logger.info(f"✅ Отменено {cancelled_count} напоминаний для {session_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка отмены напоминаний для {session_id}: {e}")
    
    async def get_session_reminders(self, session_id: str) -> List[ReminderTask]:
        """Получает все напоминания для сессии"""
        try:
            all_reminders = await self._load_reminders()
            
            session_reminders = [
                reminder for reminder in all_reminders
                if reminder.session_id == session_id
            ]
            
            # Сортируем по времени
            session_reminders.sort(key=lambda r: r.scheduled_time)
            return session_reminders
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения напоминаний для {session_id}: {e}")
            return []
    
    async def get_reminder_stats(self) -> Dict[str, Any]:
        """Получает статистику по напоминаниям"""
        try:
            all_reminders = await self._load_reminders()
            
            total_reminders = len(all_reminders)
            completed_reminders = sum(1 for r in all_reminders if r.is_completed)
            pending_reminders = total_reminders - completed_reminders
            
            # Статистика по типам
            type_stats = {}
            for reminder in all_reminders:
                reminder_type = reminder.reminder_type
                if reminder_type not in type_stats:
                    type_stats[reminder_type] = {'total': 0, 'completed': 0}
                
                type_stats[reminder_type]['total'] += 1
                if reminder.is_completed:
                    type_stats[reminder_type]['completed'] += 1
            
            # Ближайшие напоминания
            now = datetime.now()
            upcoming_reminders = [
                r for r in all_reminders 
                if not r.is_completed and r.scheduled_time > now
            ]
            upcoming_reminders.sort(key=lambda r: r.scheduled_time)
            
            return {
                'total_reminders': total_reminders,
                'completed_reminders': completed_reminders,
                'pending_reminders': pending_reminders,
                'completion_rate': (completed_reminders / max(total_reminders, 1)) * 100,
                'type_stats': type_stats,
                'upcoming_count': len(upcoming_reminders),
                'next_reminder_time': upcoming_reminders[0].scheduled_time.isoformat() if upcoming_reminders else None
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики напоминаний: {e}")
            return {}
    
    async def cleanup_old_reminders(self, days: int = 30):
        """Очищает старые выполненные напоминания"""
        try:
            all_reminders = await self._load_reminders()
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Оставляем только невыполненные или недавние напоминания
            filtered_reminders = [
                reminder for reminder in all_reminders
                if (not reminder.is_completed or 
                    reminder.scheduled_time > cutoff_date)
            ]
            
            removed_count = len(all_reminders) - len(filtered_reminders)
            
            if removed_count > 0:
                await self._save_all_reminders(filtered_reminders)
                logger.info(f"✅ Очищено {removed_count} старых напоминаний")
            
        except Exception as e:
            logger.error(f"❌ Ошибка очистки старых напоминаний: {e}")
    
    async def _save_reminders(self, reminders: List[ReminderTask]):
        """Добавляет новые напоминания в хранилище"""
        try:
            # Загружаем существующие напоминания
            all_reminders = await self._load_reminders()
            
            # Добавляем новые
            all_reminders.extend(reminders)
            
            # Сохраняем все
            await self._save_all_reminders(all_reminders)
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения напоминаний: {e}")
    
    async def _save_all_reminders(self, reminders: List[ReminderTask]):
        """Сохраняет все напоминания"""
        try:
            data = [reminder.to_dict() for reminder in reminders]
            
            with open(self.reminders_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"❌ Ошибка записи напоминаний в файл: {e}")
    
    async def _load_reminders(self) -> List[ReminderTask]:
        """Загружает все напоминания"""
        try:
            if not self.reminders_file.exists():
                return []
            
            with open(self.reminders_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            reminders = []
            for item in data:
                reminder = ReminderTask(
                    session_id=item['session_id'],
                    reminder_type=item['reminder_type'],
                    scheduled_time=datetime.fromisoformat(item['scheduled_time']),
                    message_template=item['message_template'],
                    attempt_number=item.get('attempt_number', 1),
                    max_attempts=item.get('max_attempts', 4),
                    is_completed=item.get('is_completed', False),
                    created_at=datetime.fromisoformat(item.get('created_at', datetime.now().isoformat()))
                )
                reminders.append(reminder)
            
            return reminders
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки напоминаний: {e}")
            return []