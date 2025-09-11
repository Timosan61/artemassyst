"""
Основной сервис памяти с интеграцией ZEP Cloud
"""
import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from zep_cloud.client import AsyncZep
from zep_cloud.types import Message

from .models import DialogState, LeadData, ClientType
from .extractors import LeadDataExtractor, DialogStateExtractor
from .analytics import AnalyticsService
from .reminders import ReminderService


logger = logging.getLogger(__name__)


class MemoryService:
    """Интеллектуальная система памяти с интеграцией ZEP Cloud"""
    
    def __init__(self, zep_api_key: str, enable_memory: bool = True):
        self.zep_api_key = zep_api_key
        self.enable_memory = enable_memory
        self.zep_client = None
        
        # Инициализируем AnalyticsService с ZEP API ключом
        if not zep_api_key:
            raise ValueError("ZEP API key обязателен для работы системы памяти")
        
        self.analytics = AnalyticsService(zep_api_key)
        self.reminders = ReminderService()
        
        if self.enable_memory:
            try:
                self.zep_client = AsyncZep(api_key=zep_api_key)
                logger.info("✅ Инициализирован ZEP Cloud клиент")
            except Exception as e:
                logger.error(f"❌ Ошибка инициализации ZEP Cloud: {e}")
                raise
    
    async def process_message(self, user_id: str, message_text: str, 
                            message_type: str = "user") -> Dict[str, Any]:
        """
        Обрабатывает сообщение и обновляет память
        
        Returns:
            Dict с информацией о состоянии диалога и рекомендациями
        """
        session_id = f"user_{user_id}"
        
        try:
            # Получаем текущие данные о лиде
            current_lead = await self.get_lead_data(session_id)
            
            # Извлекаем новые данные из сообщения
            updated_lead = LeadDataExtractor.extract_from_message(
                message_text, current_lead
            )
            
            # Определяем новое состояние диалога
            new_state = DialogStateExtractor.determine_state(
                message_text, updated_lead.current_dialog_state, updated_lead
            )
            
            # Обновляем статус квалификации
            qualification_status = DialogStateExtractor.calculate_qualification_status(updated_lead)
            
            # Проверяем изменения состояния
            state_changed = updated_lead.current_dialog_state != new_state
            status_changed = updated_lead.qualification_status != qualification_status
            
            # Обновляем данные
            updated_lead.current_dialog_state = new_state
            updated_lead.qualification_status = qualification_status
            
            # Сохраняем в памяти
            if self.enable_memory:
                await self._save_to_memory(session_id, message_text, updated_lead, message_type)
            
            # Сохраняем данные лида
            await self.save_lead_data(session_id, updated_lead)
            
            # Аналитика
            if state_changed:
                await self.analytics.track_event(
                    session_id, 'state_change', 
                    {'from': updated_lead.current_dialog_state.value, 'to': new_state.value}
                )
            
            if status_changed:
                await self.analytics.track_event(
                    session_id, 'qualification_change',
                    {'status': qualification_status.value}
                )
            
            # Проверяем необходимость установки напоминаний
            await self._check_reminders(session_id, updated_lead, new_state)
            
            # Генерируем рекомендации для ответа
            recommendations = await self._generate_recommendations(updated_lead, new_state)
            
            return {
                'lead_data': updated_lead,
                'current_state': new_state,
                'qualification_status': qualification_status,
                'state_changed': state_changed,
                'status_changed': status_changed,
                'recommendations': recommendations,
                'should_escalate': self._should_escalate(updated_lead),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения для {session_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'lead_data': current_lead if 'current_lead' in locals() else LeadData()
            }
    
    async def get_lead_data(self, session_id: str) -> LeadData:
        """Получает данные о лиде из памяти"""
        if not self.enable_memory:
            return LeadData()
        
        try:
            # Получаем сессию из ZEP
            session = await self.zep_client.memory.get_session(session_id)
            
            if session and hasattr(session, 'metadata') and session.metadata:
                return LeadData.from_dict(session.metadata)
            else:
                return LeadData()
                
        except Exception as e:
            logger.warning(f"⚠️ Не удалось получить данные лида для {session_id}: {e}")
            return LeadData()
    
    async def save_lead_data(self, session_id: str, lead_data: LeadData):
        """Сохраняет данные о лиде в память"""
        if not self.enable_memory:
            return
        
        try:
            # Обновляем метаданные сессии в ZEP
            await self.zep_client.memory.update_session(
                session_id=session_id,
                metadata=lead_data.to_dict()
            )
            logger.debug(f"✅ Данные лида сохранены для {session_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения данных лида для {session_id}: {e}")
    
    async def get_dialog_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Получает историю диалога"""
        if not self.enable_memory:
            return []
        
        try:
            memory = await self.zep_client.memory.get(session_id=session_id)
            
            if memory and memory.messages:
                return [
                    {
                        'role': msg.role_type,  # Используем role_type для стандартных ролей user/assistant
                        'content': msg.content,
                        'timestamp': msg.created_at,
                        'metadata': getattr(msg, 'metadata', {}),
                        'speaker_name': msg.role  # Сохраняем имя говорящего отдельно
                    }
                    for msg in memory.messages[-limit:]
                ]
            return []
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения истории для {session_id}: {e}")
            return []
    
    async def search_similar_cases(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Поиск похожих кейсов в памяти"""
        if not self.enable_memory:
            return []
        
        try:
            # Используем поиск ZEP для нахождения похожих диалогов
            results = await self.zep_client.memory.search_memory(
                session_ids=[],  # Поиск по всем сессиям
                text=query,
                limit=limit
            )
            
            return [
                {
                    'session_id': result.session_id,
                    'content': result.message.content,
                    'score': result.distance,
                    'metadata': getattr(result.message, 'metadata', {})
                }
                for result in results
            ] if results else []
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска похожих кейсов: {e}")
            return []
    
    async def _save_to_memory(self, session_id: str, message_text: str, 
                            lead_data: LeadData, message_type: str):
        """Сохраняет сообщение в ZEP память"""
        try:
            # Определяем роль и имя для сообщения
            if message_type == "user":
                role_name = f"User_{session_id.split('_')[-1][:6]}" if '_' in session_id else session_id
                role_type = "user"
            else:
                role_name = "Алёна"
                role_type = "assistant"
                
            # Создаем сообщение для ZEP
            message = Message(
                role=role_name,
                role_type=role_type,
                content=message_text,
                metadata={
                    'dialog_state': lead_data.current_dialog_state.value,
                    'qualification_status': lead_data.qualification_status.value if lead_data.qualification_status else None,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            # Добавляем сообщение в память
            await self.zep_client.memory.add(
                session_id=session_id,
                messages=[message]
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения в ZEP память для {session_id}: {e}")
    
    async def _check_reminders(self, session_id: str, lead_data: LeadData, 
                             current_state: DialogState):
        """Проверяет и устанавливает напоминания"""
        try:
            # Устанавливаем напоминания для состояния "принятие решения"
            if (current_state == DialogState.S8_ACTION and 
                lead_data.qualification_status in [ClientType.WARM, ClientType.HOT]):
                
                await self.reminders.schedule_follow_up_sequence(session_id)
            
            # Напоминание о демо для горячих клиентов
            if (lead_data.qualification_status == ClientType.HOT and 
                lead_data.agreed_demo_slots):
                
                await self.reminders.schedule_demo_reminder(
                    session_id, lead_data.agreed_demo_slots[0]
                )
                
        except Exception as e:
            logger.error(f"❌ Ошибка установки напоминаний для {session_id}: {e}")
    
    async def _generate_recommendations(self, lead_data: LeadData, 
                                     current_state: DialogState) -> Dict[str, Any]:
        """Генерирует рекомендации для следующего ответа"""
        recommendations = {
            'next_questions': [],
            'suggested_responses': [],
            'escalation_needed': False,
            'demo_ready': False
        }
        
        try:
            # Рекомендации в зависимости от состояния
            if current_state == DialogState.S0_GREETING:
                recommendations['next_questions'] = [
                    "Для себя ищете недвижимость или как инвестицию?",
                    "Вы сейчас в Сочи? Если нет — из какого города?"
                ]
            
            elif current_state == DialogState.S1_BUSINESS:
                if not lead_data.automation_goal:
                    recommendations['next_questions'] = [
                        "Для себя ищете жилье или как инвестицию?",
                        "Цель покупки: ПМЖ, сдача в аренду или сбережения?"
                    ]
            
            elif current_state == DialogState.S2_GOAL:
                if not lead_data.budget_min:
                    recommendations['next_questions'] = [
                        "На какой бюджет мне ориентироваться?",
                        "Есть решение: AI-ассистент от $350. Такой диапазон рассматриваете?"
                    ]
            
            elif current_state == DialogState.S8_ACTION:
                if lead_data.qualification_status == ClientType.HOT:
                    recommendations['demo_ready'] = True
                    recommendations['suggested_responses'] = [
                        "Готовы на демо-показ? Сегодня в 15:30 или 18:00?",
                        "Чтобы прислать презентацию, подскажите номер WhatsApp: +7..."
                    ]
            
            # Проверяем необходимость эскалации
            recommendations['escalation_needed'] = self._should_escalate(lead_data)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации рекомендаций: {e}")
            return recommendations
    
    def _should_escalate(self, lead_data: LeadData) -> bool:
        """Определяет, нужна ли эскалация к живому менеджеру"""
        escalation_conditions = [
            # Горячий клиент
            lead_data.qualification_status == ClientType.HOT,
            
            # Есть телефон и готов к демо
            bool(lead_data.phone) and bool(lead_data.agreed_demo_slots),
            
            # Запросил презентацию/детали
            'презентация' in (lead_data.comments or '').lower(),
            
            # Специфические технические требования
            len(lead_data.technical_requirements) > 3,
            
            # Высокий бюджет
            (lead_data.budget_min and lead_data.budget_min > 1000) or
            (lead_data.budget_max and lead_data.budget_max > 2000)
        ]
        
        return any(escalation_conditions)
    
    async def get_analytics_summary(self, session_id: str) -> Dict[str, Any]:
        """Получает сводку аналитики по сессии"""
        try:
            events = await self.analytics.get_session_events(session_id)
            lead_data = await self.get_lead_data(session_id)
            
            return {
                'total_events': len(events),
                'current_state': lead_data.current_dialog_state.value,
                'qualification_status': lead_data.qualification_status.value if lead_data.qualification_status else None,
                'data_completeness': self._calculate_data_completeness(lead_data),
                'escalation_score': self._calculate_escalation_score(lead_data),
                'last_activity': lead_data.updated_at.isoformat(),
                'events': events[-10:]  # Последние 10 событий
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения аналитики для {session_id}: {e}")
            return {}
    
    def _calculate_data_completeness(self, lead_data: LeadData) -> float:
        """Вычисляет полноту данных (0-1)"""
        total_fields = 20  # Общее количество важных полей
        filled_fields = 0
        
        # Считаем заполненные поля
        if lead_data.name: filled_fields += 1
        if lead_data.phone: filled_fields += 1
        if lead_data.business_sphere: filled_fields += 1
        if lead_data.automation_goal: filled_fields += 1
        if lead_data.payment_type: filled_fields += 1
        if lead_data.budget_min or lead_data.budget_max: filled_fields += 2
        if lead_data.technical_requirements: filled_fields += 1
        if lead_data.urgency_level: filled_fields += 1
        if lead_data.automation_experience: filled_fields += 1
        if lead_data.preferred_contact_method: filled_fields += 1
        # ... другие поля
        
        return filled_fields / total_fields
    
    def _calculate_escalation_score(self, lead_data: LeadData) -> float:
        """Вычисляет скор для эскалации (0-1)"""
        score = 0.0
        
        # Статус квалификации
        if lead_data.qualification_status == ClientType.HOT:
            score += 0.4
        elif lead_data.qualification_status == ClientType.WARM:
            score += 0.2
        
        # Контактная информация
        if lead_data.phone:
            score += 0.2
        
        # Бюджет
        if lead_data.budget_max and lead_data.budget_max > 1000:
            score += 0.2
        
        # Срочность
        if lead_data.urgency_level == 'high':
            score += 0.2
        
        return min(score, 1.0)