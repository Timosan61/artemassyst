"""
Модели данных для интеллектуальной системы памяти ZEP
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class DialogState(Enum):
    """Состояния диалога"""
    S0_GREETING = "s0_greeting"           # Приветствие + выяснение цели
    S1_BUSINESS = "s1_business"           # Местоположение + город
    S2_GOAL = "s2_goal"                   # Цель покупки недвижимости
    S3_PAYMENT = "s3_payment"             # Форма оплаты и бюджет
    S4_REQUIREMENTS = "s4_requirements"   # Требования к объекту
    S5_BUDGET = "s5_budget"               # Уточнение бюджета
    S6_URGENCY = "s6_urgency"             # Срочность покупки
    S7_EXPERIENCE = "s7_experience"       # Опыт покупки в Сочи
    S8_ACTION = "s8_action"               # Онлайн-показ или встреча


class ClientType(Enum):
    """Типы клиентов"""
    COLD = "cold"      # Холодный - 1 из 3 критериев
    WARM = "warm"      # Тёплый - 2 из 3 критериев
    HOT = "hot"        # Горячий - 3 из 3 критерия


class AutomationGoal(Enum):
    """Цели покупки недвижимости"""
    SHORT_INVESTMENT = "short_investment"     # Короткие инвестиции (до 12 мес)
    LONG_INVESTMENT = "long_investment"       # Длинные инвестиции (12+ мес)
    RESIDENCE = "residence"                   # ПМЖ (переезд/сезонно)
    SAVINGS = "savings"                       # Сбережения (сохранение капитала)
    RENTAL_BUSINESS = "rental_business"       # Арендный бизнес


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
    city: Optional[str] = None  # Откуда клиент (Волгодонск, Москва и т.д.)
    current_location: Optional[str] = None  # Где сейчас находится
    is_in_sochi: Optional[bool] = None  # Находится ли в Сочи сейчас
    is_local: Optional[bool] = None  # Местный житель Сочи или нет
    
    # ДОПОЛНИТЕЛЬНЫЕ ПОЛЯ из инструкции по недвижимости
    rooms_count: Optional[int] = None  # Количество комнат
    area_min: Optional[int] = None  # Минимальная площадь
    area_max: Optional[int] = None  # Максимальная площадь
    view_preference: Optional[str] = None  # Вид: море, горы, парк
    completion_date: Optional[str] = None  # Срок сдачи объекта
    need_remote_deal: Optional[bool] = None  # Нужна удалённая сделка
    online_viewing_ready: Optional[bool] = None  # Готовность к онлайн-показу
    need_to_sell_current: Optional[bool] = None  # Нужна продажа своей недвижимости
    current_property_city: Optional[str] = None  # Город текущей недвижимости для продажи
    decision_maker: Optional[str] = None  # С кем принимает решение о покупке (супруг/супруга, партнер, сам)
    
    # Бизнес-информация
    business_sphere: Optional[str] = None
    company_size: Optional[str] = None
    current_automation_tasks: Optional[str] = None
    
    # Потребности и бюджет
    automation_goal: Optional[AutomationGoal] = None  # Цель покупки (инвестиции/ПМЖ и т.д.)
    payment_type: Optional[PaymentType] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    mortgage_bank: Optional[str] = None  # Банк для ипотеки
    needs_sell_own: Optional[bool] = None  # Нужна ли продажа своей недвижимости
    
    # Недвижимость
    preferred_locations: List[str] = field(default_factory=list)  # Красная Поляна, Сириус и т.д.
    property_type: Optional[str] = None  # дом, квартира, апартаменты, участок
    property_params: Dict[str, Any] = field(default_factory=dict)  # комнаты, метраж, вид и т.д.
    
    # Технические требования (старые поля для совместимости)
    technical_requirements: List[str] = field(default_factory=list)
    automation_type: List[str] = field(default_factory=list)  # чат-бот, CRM, email, соцсети
    
    # Временные рамки
    implementation_date: Optional[datetime] = None
    urgency_level: Optional[str] = None  # high, medium, low
    ready_for_quick_decision: Optional[bool] = None
    urgency_date: Optional[str] = None  # Дата приезда в Сочи
    
    # Опыт и готовность
    automation_experience: Optional[str] = None  # none, some, experienced
    needs_remote_setup: Optional[bool] = None
    online_show_ready: Optional[bool] = None  # Готовность к онлайн-показу
    sochi_experience: Optional[str] = None  # Опыт покупки в Сочи
    
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
            'current_location': self.current_location,
            'is_in_sochi': self.is_in_sochi,
            'is_local': self.is_local,
            'rooms_count': self.rooms_count,
            'area_min': self.area_min,
            'area_max': self.area_max,
            'view_preference': self.view_preference,
            'completion_date': self.completion_date,
            'need_remote_deal': self.need_remote_deal,
            'online_viewing_ready': self.online_viewing_ready,
            'need_to_sell_current': self.need_to_sell_current,
            'current_property_city': self.current_property_city,
            'decision_maker': self.decision_maker,
            'business_sphere': self.business_sphere,
            'company_size': self.company_size,
            'current_automation_tasks': self.current_automation_tasks,
            'automation_goal': self.automation_goal.value if self.automation_goal else None,
            'payment_type': self.payment_type.value if self.payment_type else None,
            'budget_min': self.budget_min,
            'budget_max': self.budget_max,
            'mortgage_bank': self.mortgage_bank,
            'needs_sell_own': self.needs_sell_own,
            'preferred_locations': self.preferred_locations,
            'property_type': self.property_type,
            'property_params': self.property_params,
            'technical_requirements': self.technical_requirements,
            'automation_type': self.automation_type,
            'implementation_date': self.implementation_date.isoformat() if self.implementation_date else None,
            'urgency_level': self.urgency_level,
            'ready_for_quick_decision': self.ready_for_quick_decision,
            'urgency_date': self.urgency_date,
            'automation_experience': self.automation_experience,
            'needs_remote_setup': self.needs_remote_setup,
            'online_show_ready': self.online_show_ready,
            'sochi_experience': self.sochi_experience,
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
        lead.current_location = data.get('current_location')
        lead.is_in_sochi = data.get('is_in_sochi')
        lead.is_local = data.get('is_local')
        
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
        lead.mortgage_bank = data.get('mortgage_bank')
        lead.needs_sell_own = data.get('needs_sell_own')
        
        # Недвижимость
        lead.preferred_locations = data.get('preferred_locations', [])
        lead.property_type = data.get('property_type')
        lead.property_params = data.get('property_params', {})
        
        # Технические требования
        lead.technical_requirements = data.get('technical_requirements', [])
        lead.automation_type = data.get('automation_type', [])
        
        # Временные рамки
        if data.get('implementation_date'):
            lead.implementation_date = datetime.fromisoformat(data['implementation_date'])
        
        lead.urgency_level = data.get('urgency_level')
        lead.ready_for_quick_decision = data.get('ready_for_quick_decision')
        lead.urgency_date = data.get('urgency_date')
        
        # Опыт и готовность
        lead.automation_experience = data.get('automation_experience')
        lead.needs_remote_setup = data.get('needs_remote_setup')
        lead.online_show_ready = data.get('online_show_ready')
        lead.sochi_experience = data.get('sochi_experience')
        
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