"""
Модели данных для интеллектуальной системы памяти ZEP
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class DialogState(Enum):
    """Состояния диалога"""
    S0_GREETING = "s0_greeting"           # Приветствие + мини-ценность
    S1_BUSINESS = "s1_business"           # Сфера + местонахождение
    S2_GOAL = "s2_goal"                   # Цель автоматизации
    S3_PAYMENT = "s3_payment"             # Форма оплаты и бюджет
    S4_REQUIREMENTS = "s4_requirements"   # Технические требования
    S5_BUDGET = "s5_budget"               # Уточнение бюджета
    S6_URGENCY = "s6_urgency"             # Срочность
    S7_EXPERIENCE = "s7_experience"       # Опыт автоматизации
    S8_ACTION = "s8_action"               # Следующее действие


class ClientType(Enum):
    """Типы клиентов"""
    COLD = "cold"      # Холодный - 1 из 3 критериев
    WARM = "warm"      # Тёплый - 2 из 3 критериев
    HOT = "hot"        # Горячий - 3 из 3 критерия


class AutomationGoal(Enum):
    """Цели автоматизации"""
    TIME_SAVING = "time_saving"           # Экономия времени
    SALES_INCREASE = "sales_increase"     # Увеличение продаж
    COST_REDUCTION = "cost_reduction"     # Снижение затрат
    QUALITY_IMPROVEMENT = "quality_improvement"  # Улучшение качества
    SCALING = "scaling"                   # Масштабирование


class PaymentType(Enum):
    """Формы оплаты"""
    CASH = "cash"               # Наличные
    CARDS = "cards"             # Карты
    BANK_TRANSFER = "bank_transfer"  # Безнал
    CRYPTO = "crypto"           # Криптовалюта


@dataclass
class LeadData:
    """Данные о лиде"""
    # Базовая информация
    name: Optional[str] = None
    phone: Optional[str] = None
    telegram_username: Optional[str] = None
    whatsapp: Optional[str] = None
    city: Optional[str] = None
    
    # Бизнес-информация
    business_sphere: Optional[str] = None
    company_size: Optional[str] = None
    current_automation_tasks: Optional[str] = None
    
    # Потребности и бюджет
    automation_goal: Optional[AutomationGoal] = None
    payment_type: Optional[PaymentType] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    
    # Технические требования
    technical_requirements: List[str] = field(default_factory=list)
    automation_type: List[str] = field(default_factory=list)  # чат-бот, CRM, email, соцсети
    
    # Временные рамки
    implementation_date: Optional[datetime] = None
    urgency_level: Optional[str] = None  # high, medium, low
    ready_for_quick_decision: Optional[bool] = None
    
    # Опыт и готовность
    automation_experience: Optional[str] = None  # none, some, experienced
    needs_remote_setup: Optional[bool] = None
    
    # Коммуникация
    preferred_contact_time: Optional[str] = None
    preferred_contact_method: Optional[str] = None
    agreed_demo_slots: List[datetime] = field(default_factory=list)
    
    # Статус
    qualification_status: Optional[ClientType] = None
    current_dialog_state: DialogState = DialogState.S0_GREETING
    
    # Метаданные
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    utm_source: Optional[str] = None
    comments: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для ZEP"""
        return {
            'name': self.name,
            'phone': self.phone,
            'telegram_username': self.telegram_username,
            'whatsapp': self.whatsapp,
            'city': self.city,
            'business_sphere': self.business_sphere,
            'company_size': self.company_size,
            'current_automation_tasks': self.current_automation_tasks,
            'automation_goal': self.automation_goal.value if self.automation_goal else None,
            'payment_type': self.payment_type.value if self.payment_type else None,
            'budget_min': self.budget_min,
            'budget_max': self.budget_max,
            'technical_requirements': self.technical_requirements,
            'automation_type': self.automation_type,
            'implementation_date': self.implementation_date.isoformat() if self.implementation_date else None,
            'urgency_level': self.urgency_level,
            'ready_for_quick_decision': self.ready_for_quick_decision,
            'automation_experience': self.automation_experience,
            'needs_remote_setup': self.needs_remote_setup,
            'preferred_contact_time': self.preferred_contact_time,
            'preferred_contact_method': self.preferred_contact_method,
            'agreed_demo_slots': [slot.isoformat() for slot in self.agreed_demo_slots],
            'qualification_status': self.qualification_status.value if self.qualification_status else None,
            'current_dialog_state': self.current_dialog_state.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'utm_source': self.utm_source,
            'comments': self.comments
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LeadData':
        """Создание объекта из словаря"""
        lead = cls()
        
        # Базовая информация
        lead.name = data.get('name')
        lead.phone = data.get('phone')
        lead.telegram_username = data.get('telegram_username')
        lead.whatsapp = data.get('whatsapp')
        lead.city = data.get('city')
        
        # Бизнес-информация
        lead.business_sphere = data.get('business_sphere')
        lead.company_size = data.get('company_size')
        lead.current_automation_tasks = data.get('current_automation_tasks')
        
        # Потребности и бюджет
        if data.get('automation_goal'):
            lead.automation_goal = AutomationGoal(data['automation_goal'])
        if data.get('payment_type'):
            lead.payment_type = PaymentType(data['payment_type'])
        
        lead.budget_min = data.get('budget_min')
        lead.budget_max = data.get('budget_max')
        
        # Технические требования
        lead.technical_requirements = data.get('technical_requirements', [])
        lead.automation_type = data.get('automation_type', [])
        
        # Временные рамки
        if data.get('implementation_date'):
            lead.implementation_date = datetime.fromisoformat(data['implementation_date'])
        
        lead.urgency_level = data.get('urgency_level')
        lead.ready_for_quick_decision = data.get('ready_for_quick_decision')
        
        # Опыт и готовность
        lead.automation_experience = data.get('automation_experience')
        lead.needs_remote_setup = data.get('needs_remote_setup')
        
        # Коммуникация
        lead.preferred_contact_time = data.get('preferred_contact_time')
        lead.preferred_contact_method = data.get('preferred_contact_method')
        
        if data.get('agreed_demo_slots'):
            lead.agreed_demo_slots = [
                datetime.fromisoformat(slot) 
                for slot in data['agreed_demo_slots']
            ]
        
        # Статус
        if data.get('qualification_status'):
            lead.qualification_status = ClientType(data['qualification_status'])
        if data.get('current_dialog_state'):
            lead.current_dialog_state = DialogState(data['current_dialog_state'])
        
        # Метаданные
        if data.get('created_at'):
            lead.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            lead.updated_at = datetime.fromisoformat(data['updated_at'])
        
        lead.utm_source = data.get('utm_source')
        lead.comments = data.get('comments', '')
        
        return lead


@dataclass
class ReminderTask:
    """Задача для напоминания"""
    session_id: str
    reminder_type: str  # follow_up, demo_reminder, etc.
    scheduled_time: datetime
    message_template: str
    attempt_number: int = 1
    max_attempts: int = 4
    is_completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'session_id': self.session_id,
            'reminder_type': self.reminder_type,
            'scheduled_time': self.scheduled_time.isoformat(),
            'message_template': self.message_template,
            'attempt_number': self.attempt_number,
            'max_attempts': self.max_attempts,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat()
        }


@dataclass 
class AnalyticsData:
    """Данные аналитики"""
    session_id: str
    event_type: str  # state_change, qualification_update, etc.
    event_data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'session_id': self.session_id,
            'event_type': self.event_type,
            'event_data': self.event_data,
            'timestamp': self.timestamp.isoformat()
        }