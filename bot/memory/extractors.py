"""
Экстракторы данных из диалогов для системы памяти
"""
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta

from .models import (
    DialogState, ClientType, AutomationGoal, 
    PaymentType, LeadData
)


class LeadDataExtractor:
    """Экстрактор данных о лиде из сообщений"""
    
    # Паттерны для извлечения информации
    PHONE_PATTERN = re.compile(r'\+?[78][\s\-]?\(?(\d{3})\)?\s?[\s\-]?(\d{3})[\s\-]?(\d{2})[\s\-]?(\d{2})')
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    
    # Словари для определения типов по ключевым словам
    BUSINESS_SPHERES = {
        'интернет-магазин': 'ecommerce',
        'магазин': 'retail', 
        'недвижимость': 'real_estate',
        'услуги': 'services',
        'производство': 'manufacturing',
        'кафе': 'food_service',
        'ресторан': 'food_service',
        'салон': 'beauty',
        'клиника': 'medical',
        'стоматология': 'medical',
        'автосервис': 'automotive',
        'строительство': 'construction',
        'консалтинг': 'consulting',
        'обучение': 'education',
        'фитнес': 'fitness',
        'туризм': 'tourism'
    }
    
    AUTOMATION_GOALS = {
        'краткосрочные инвестиции': AutomationGoal.SHORT_INVESTMENT,
        'короткие инвестиции': AutomationGoal.SHORT_INVESTMENT,
        'на год': AutomationGoal.SHORT_INVESTMENT,
        'долгосрочные инвестиции': AutomationGoal.LONG_INVESTMENT,
        'длинные инвестиции': AutomationGoal.LONG_INVESTMENT,
        'на долго': AutomationGoal.LONG_INVESTMENT,
        'для проживания': AutomationGoal.RESIDENCE,
        'для жизни': AutomationGoal.RESIDENCE,
        'пмж': AutomationGoal.RESIDENCE,
        'переезд': AutomationGoal.RESIDENCE,
        'сбережения': AutomationGoal.SAVINGS,
        'сохранить капитал': AutomationGoal.SAVINGS,
        'сохранение': AutomationGoal.SAVINGS,
        'арендный бизнес': AutomationGoal.RENTAL_BUSINESS,
        'сдавать в аренду': AutomationGoal.RENTAL_BUSINESS,
        'аренда': AutomationGoal.RENTAL_BUSINESS
    }
    
    PAYMENT_TYPES = {
        'наличные': PaymentType.CASH,
        'наличными': PaymentType.CASH,
        'карта': PaymentType.CARDS,
        'карты': PaymentType.CARDS,
        'картой': PaymentType.CARDS,
        'безнал': PaymentType.BANK_TRANSFER,
        'безналичный': PaymentType.BANK_TRANSFER,
        'банк': PaymentType.BANK_TRANSFER,
        'перевод': PaymentType.BANK_TRANSFER,
        'крипта': PaymentType.CRYPTO,
        'криптовалюта': PaymentType.CRYPTO,
        'биткоин': PaymentType.CRYPTO
    }
    
    BUDGET_PATTERNS = [
        re.compile(r'(\d+)\s*(?:тысяч|тыс|k)', re.IGNORECASE),
        re.compile(r'(\d+)\s*(?:миллион|млн|m)', re.IGNORECASE),
        re.compile(r'(\d+)\s*(?:долларов?|\$|usd)', re.IGNORECASE),
        re.compile(r'(\d+)\s*(?:рублей?|руб|₽)', re.IGNORECASE),
        re.compile(r'до\s+(\d+)', re.IGNORECASE),
        re.compile(r'от\s+(\d+)\s+до\s+(\d+)', re.IGNORECASE),
        re.compile(r'(\d+)\s*-\s*(\d+)', re.IGNORECASE),
    ]
    
    @classmethod
    def extract_from_message(cls, message: str, current_lead: Optional[LeadData] = None) -> LeadData:
        """Извлекает данные из сообщения"""
        lead = current_lead or LeadData()
        message_lower = message.lower()
        
        # Извлечение контактной информации
        cls._extract_contacts(message, lead)
        
        # Извлечение бизнес-информации
        cls._extract_business_info(message_lower, lead)
        
        # Извлечение целей покупки недвижимости
        cls._extract_automation_goals(message_lower, lead)
        
        # Извлечение информации об оплате
        cls._extract_payment_info(message_lower, lead)
        
        # Извлечение бюджета
        cls._extract_budget(message_lower, lead)
        
        # Извлечение технических требований
        cls._extract_technical_requirements(message_lower, lead)
        
        # Извлечение временной информации
        cls._extract_time_info(message_lower, lead)
        
        # Обновление времени
        lead.updated_at = datetime.now()
        
        return lead
    
    @classmethod
    def _extract_contacts(cls, message: str, lead: LeadData):
        """Извлечение контактной информации"""
        # Телефон
        if not lead.phone:
            phone_match = cls.PHONE_PATTERN.search(message)
            if phone_match:
                lead.phone = f"+7{phone_match.group(1)}{phone_match.group(2)}{phone_match.group(3)}{phone_match.group(4)}"
        
        # Email
        email_match = cls.EMAIL_PATTERN.search(message)
        if email_match:
            # Предполагаем, что email может быть именем пользователя Telegram
            lead.telegram_username = email_match.group(0)
        
        # Имя (простая эвристика - первое слово в сообщении, если это не стандартные фразы)
        words = message.split()
        if words and not lead.name:
            first_word = words[0].strip('.,!?').title()
            if (len(first_word) > 2 and 
                first_word.lower() not in ['привет', 'здравствуйте', 'добрый', 'меня', 'интересует']):
                lead.name = first_word
    
    @classmethod
    def _extract_business_info(cls, message_lower: str, lead: LeadData):
        """Извлечение информации о бизнесе"""
        # Сфера бизнеса
        if not lead.business_sphere:
            for keyword, sphere in cls.BUSINESS_SPHERES.items():
                if keyword in message_lower:
                    lead.business_sphere = sphere
                    break
        
        # Размер компании (эвристика)
        if 'один' in message_lower or 'сам' in message_lower or 'ип' in message_lower:
            lead.company_size = 'individual'
        elif 'команда' in message_lower or 'сотрудник' in message_lower:
            lead.company_size = 'small_team'
        elif 'офис' in message_lower or 'компания' in message_lower:
            lead.company_size = 'company'
    
    @classmethod 
    def _extract_automation_goals(cls, message_lower: str, lead: LeadData):
        """Извлечение целей покупки недвижимости"""
        if not lead.automation_goal:
            for keyword, goal in cls.AUTOMATION_GOALS.items():
                if keyword in message_lower:
                    lead.automation_goal = goal
                    break
    
    @classmethod
    def _extract_payment_info(cls, message_lower: str, lead: LeadData):
        """Извлечение информации об оплате"""
        if not lead.payment_type:
            for keyword, payment in cls.PAYMENT_TYPES.items():
                if keyword in message_lower:
                    lead.payment_type = payment
                    break
    
    @classmethod
    def _extract_budget(cls, message_lower: str, lead: LeadData):
        """Извлечение информации о бюджете"""
        if lead.budget_min and lead.budget_max:
            return  # Бюджет уже определен
        
        for pattern in cls.BUDGET_PATTERNS:
            match = pattern.search(message_lower)
            if match:
                if len(match.groups()) == 1:  # Одно число
                    amount = int(match.group(1))
                    if 'до' in match.group(0):
                        lead.budget_max = amount
                    else:
                        lead.budget_min = amount
                elif len(match.groups()) == 2:  # Диапазон
                    lead.budget_min = int(match.group(1))
                    lead.budget_max = int(match.group(2))
                break
    
    @classmethod
    def _extract_technical_requirements(cls, message_lower: str, lead: LeadData):
        """Извлечение технических требований"""
        tech_keywords = {
            'crm': 'CRM интеграция',
            'сайт': 'Интеграция с сайтом',
            'instagram': 'Instagram',
            'whatsapp': 'WhatsApp',
            'telegram': 'Telegram',
            'email': 'Email рассылки',
            'чат-бот': 'Чат-бот',
            'бот': 'Чат-бот',
            'автоответчик': 'Автоответчик',
            'воронка': 'Воронка продаж'
        }
        
        for keyword, requirement in tech_keywords.items():
            if keyword in message_lower and requirement not in lead.technical_requirements:
                lead.technical_requirements.append(requirement)
    
    @classmethod
    def _extract_time_info(cls, message_lower: str, lead: LeadData):
        """Извлечение временной информации"""
        # Срочность
        urgency_keywords = {
            'срочно': 'high',
            'быстро': 'high', 
            'асап': 'high',
            'завтра': 'high',
            'сегодня': 'high',
            'на неделе': 'medium',
            'в течение месяца': 'medium',
            'не спешу': 'low',
            'подумаю': 'low'
        }
        
        if not lead.urgency_level:
            for keyword, urgency in urgency_keywords.items():
                if keyword in message_lower:
                    lead.urgency_level = urgency
                    break


class DialogStateExtractor:
    """Экстрактор состояния диалога"""
    
    # Паттерны для определения состояний
    STATE_PATTERNS = {
        DialogState.S0_GREETING: [
            'привет', 'здравствуйте', 'добрый', 'начать', 'старт'
        ],
        DialogState.S1_BUSINESS: [
            'бизнес', 'компания', 'работаю', 'сфера', 'деятельность', 'занимаюсь'
        ],
        DialogState.S2_GOAL: [
            'цель', 'хочу', 'нужно', 'автоматизировать', 'экономия', 'увеличение', 'продажи'
        ],
        DialogState.S3_PAYMENT: [
            'оплата', 'деньги', 'стоимость', 'цена', 'бюджет', 'сколько'
        ],
        DialogState.S4_REQUIREMENTS: [
            'требования', 'нужна', 'интеграция', 'crm', 'сайт', 'функции'
        ],
        DialogState.S5_BUDGET: [
            'рублей', 'долларов', 'тысяч', 'млн', 'бюджет', 'до', 'от'
        ],
        DialogState.S6_URGENCY: [
            'срочно', 'быстро', 'когда', 'сроки', 'время', 'готов'
        ],
        DialogState.S7_EXPERIENCE: [
            'опыт', 'раньше', 'уже', 'использовал', 'знаю', 'первый раз'
        ],
        DialogState.S8_ACTION: [
            'демо', 'показать', 'звонок', 'встреча', 'время', 'договариваемся'
        ]
    }
    
    @classmethod
    def determine_state(cls, message: str, current_state: DialogState, lead_data: LeadData) -> DialogState:
        """Определяет следующее состояние диалога"""
        message_lower = message.lower()
        
        # Логика переходов между состояниями
        return cls._get_next_state(message_lower, current_state, lead_data)
    
    @classmethod
    def _get_next_state(cls, message: str, current_state: DialogState, lead: LeadData) -> DialogState:
        """Определяет следующее состояние на основе текущего и данных"""
        
        # Проверяем, что мы собрали на текущем этапе
        if current_state == DialogState.S0_GREETING:
            if any(word in message for word in cls.STATE_PATTERNS[DialogState.S1_BUSINESS]):
                return DialogState.S1_BUSINESS
        
        elif current_state == DialogState.S1_BUSINESS:
            if lead.business_sphere:  # Сфера определена
                if any(word in message for word in cls.STATE_PATTERNS[DialogState.S2_GOAL]):
                    return DialogState.S2_GOAL
        
        elif current_state == DialogState.S2_GOAL:
            if lead.automation_goal:  # Цель определена
                if any(word in message for word in cls.STATE_PATTERNS[DialogState.S3_PAYMENT]):
                    return DialogState.S3_PAYMENT
        
        elif current_state == DialogState.S3_PAYMENT:
            if any(word in message for word in cls.STATE_PATTERNS[DialogState.S4_REQUIREMENTS]):
                return DialogState.S4_REQUIREMENTS
        
        elif current_state == DialogState.S4_REQUIREMENTS:
            if any(word in message for word in cls.STATE_PATTERNS[DialogState.S5_BUDGET]):
                return DialogState.S5_BUDGET
        
        elif current_state == DialogState.S5_BUDGET:
            if lead.budget_min or lead.budget_max:  # Бюджет определен
                if any(word in message for word in cls.STATE_PATTERNS[DialogState.S6_URGENCY]):
                    return DialogState.S6_URGENCY
        
        elif current_state == DialogState.S6_URGENCY:
            if lead.urgency_level:  # Срочность определена
                if any(word in message for word in cls.STATE_PATTERNS[DialogState.S7_EXPERIENCE]):
                    return DialogState.S7_EXPERIENCE
        
        elif current_state == DialogState.S7_EXPERIENCE:
            if any(word in message for word in cls.STATE_PATTERNS[DialogState.S8_ACTION]):
                return DialogState.S8_ACTION
        
        # По умолчанию остаемся в текущем состоянии
        return current_state
    
    @classmethod
    def calculate_qualification_status(cls, lead: LeadData) -> ClientType:
        """Вычисляет статус квалификации: Деньги + Срочность + Понимание запроса"""
        score = 0
        
        # Деньги (бюджет определен)
        if lead.budget_min or lead.budget_max:
            score += 1
        
        # Срочность
        if lead.urgency_level in ['high', 'medium']:
            score += 1
        
        # Понимание запроса (цель и техтребования определены)
        if lead.automation_goal and (lead.technical_requirements or lead.automation_type):
            score += 1
        
        # Определяем тип клиента
        if score == 3:
            return ClientType.HOT
        elif score == 2:
            return ClientType.WARM
        else:
            return ClientType.COLD