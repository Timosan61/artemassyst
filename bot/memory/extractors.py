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
        'ипотека': PaymentType.BANK_TRANSFER,  # Добавлено
        'ипотеку': PaymentType.BANK_TRANSFER,  # Добавлено
        'ипотечный': PaymentType.BANK_TRANSFER,  # Добавлено
        'рассрочка': PaymentType.BANK_TRANSFER,  # Добавлено
        'рассрочку': PaymentType.BANK_TRANSFER,  # Добавлено
        'кредит': PaymentType.BANK_TRANSFER,  # Добавлено
        'крипта': PaymentType.CRYPTO,
        'криптовалюта': PaymentType.CRYPTO,
        'биткоин': PaymentType.CRYPTO
    }
    
    # Локации в Сочи
    SOCHI_LOCATIONS = [
        'центр', 'центральный', 'адлер', 'адлерский',
        'сириус', 'имеретинская', 'имеретинский',
        'красная поляна', 'красная', 'поляна', 'роза хутор',
        'эсто-садок', 'хоста', 'мацеста', 'дагомыс',
        'лазаревское', 'лоо', 'вардане', 'головинка',
        'у моря', 'морской', 'побережье', 'пляж'
    ]
    
    # Типы недвижимости
    PROPERTY_TYPES = {
        'дом': 'дом',
        'дома': 'дом',
        'коттедж': 'дом',
        'таунхаус': 'дом',
        'квартира': 'квартира',
        'квартиру': 'квартира',
        'студия': 'квартира',
        'апартаменты': 'апартаменты',
        'апарт': 'апартаменты',
        'участок': 'участок',
        'земля': 'участок',
        'земельный': 'участок'
    }
    
    BUDGET_PATTERNS = [
        re.compile(r'до\s+(\d+)\s*(?:млн|миллион)', re.IGNORECASE),
        re.compile(r'до\s+(\d+)\s*(?:тыс|тысяч|k)', re.IGNORECASE),
        re.compile(r'до\s+(\d+)', re.IGNORECASE),
        re.compile(r'(\d+)\s*(?:тысяч|тыс|k)', re.IGNORECASE),
        re.compile(r'(\d+)\s*(?:миллион|млн|m)', re.IGNORECASE),
        re.compile(r'(\d+)\s*(?:долларов?|\$|usd)', re.IGNORECASE),
        re.compile(r'(\d+)\s*(?:рублей?|руб|₽)', re.IGNORECASE),
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
        
        # Извлечение имени из контекста
        cls._extract_name_from_context(message, lead)
        
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
        
        # НОВЫЕ ИЗВЛЕЧЕНИЯ
        # Извлечение города и локации (передаем оригинальное сообщение)
        cls._extract_location_info(message, lead)
        
        # Извлечение локаций Сочи
        cls._extract_sochi_locations(message_lower, lead)
        
        # Извлечение типа недвижимости
        cls._extract_property_type(message_lower, lead)
        
        # Извлечение банка для ипотеки
        cls._extract_mortgage_bank(message_lower, lead)
        
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
        
        # Имя НЕ извлекается автоматически из сообщений в этой версии
        # Это должно передаваться извне (от Telegram username или другим способом)
        # Автоматическое извлечение имени отключено для избежания ошибок типа "Красная"
        pass
    
    @classmethod
    def _extract_name_from_context(cls, message: str, lead: LeadData):
        """Извлечение имени из контекста диалога - ОТКЛЮЧЕНО"""
        # ОТКЛЮЧАЕМ автоматическое извлечение имени, так как оно дает ложные срабатывания
        # "Красная поляна" не должно быть именем "Красная"
        # Имя должно передаваться из Telegram username или вводиться явно пользователем
        pass
    
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
                    
                    # Конвертируем в рубли если нужно
                    if 'тыс' in match.group(0) or 'k' in match.group(0).lower():
                        amount = amount * 1000
                    elif 'млн' in match.group(0) or 'миллион' in match.group(0) or 'm' in match.group(0).lower():
                        amount = amount * 1000000
                    elif '$' in match.group(0) or 'usd' in match.group(0).lower() or 'доллар' in match.group(0):
                        amount = amount * 90  # Примерный курс доллара
                    
                    if 'до' in match.group(0):
                        lead.budget_max = amount
                    else:
                        lead.budget_min = amount
                elif len(match.groups()) == 2:  # Диапазон
                    min_amount = int(match.group(1))
                    max_amount = int(match.group(2))
                    
                    # Конвертируем в рубли
                    if 'тыс' in match.group(0) or 'k' in match.group(0).lower():
                        min_amount = min_amount * 1000
                        max_amount = max_amount * 1000
                    elif 'млн' in match.group(0) or 'миллион' in match.group(0) or 'm' in match.group(0).lower():
                        min_amount = min_amount * 1000000
                        max_amount = max_amount * 1000000
                    
                    lead.budget_min = min_amount
                    lead.budget_max = max_amount
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
    
    @classmethod
    def _extract_location_info(cls, message: str, lead: LeadData):
        """Извлечение информации о городе и локации клиента"""
        message_lower = message.lower()
        
        # Проверяем, находится ли в Сочи
        if any(word in message_lower for word in ['в сочи', 'нахожусь в сочи', 'живу в сочи', 'я в сочи']):
            lead.is_in_sochi = True
            lead.current_location = 'Сочи'
            
            # Проверяем, местный ли
            if any(word in message_lower for word in ['живу в сочи', 'местный', 'проживаю в сочи']):
                lead.is_local = True
        elif any(word in message_lower for word in ['не в сочи', 'из москвы', 'из питера', 'из казани']):
            lead.is_in_sochi = False
        
        # Извлекаем город откуда клиент - используем ОРИГИНАЛЬНОЕ сообщение для сохранения регистра
        # Паттерн: "из Волгодонск", "из Москвы" и т.д.
        city_pattern = re.compile(r'из\s+([А-Яа-яЁё]+)', re.IGNORECASE)
        match = city_pattern.search(message)
        if match:
            city = match.group(1).strip()
            # Не сохраняем Сочи как город клиента
            if 'сочи' not in city.lower():
                lead.city = city.title()
        
        # Извлекаем дату приезда
        if 'завтра' in message_lower:
            lead.urgency_date = 'завтра'
        elif 'послезавтра' in message_lower or 'после завтра' in message_lower:
            lead.urgency_date = 'послезавтра'
        elif 'на неделе' in message_lower:
            lead.urgency_date = 'на этой неделе'
    
    @classmethod
    def _extract_sochi_locations(cls, message_lower: str, lead: LeadData):
        """Извлечение предпочитаемых локаций в Сочи"""
        found_locations = []
        
        # Проверяем особые случаи сначала (все склонения Красной Поляны)
        if any(phrase in message_lower for phrase in [
            'красная поляна', 'красную поляну', 'красной поляне', 'красной поляны'
        ]):
            found_locations.append('Красная Поляна')
        elif 'красная' in message_lower and 'поляна' in message_lower:
            found_locations.append('Красная Поляна')
        elif 'красной' in message_lower and 'поляне' in message_lower:
            found_locations.append('Красная Поляна')
        
        # Проверяем остальные локации
        for location in cls.SOCHI_LOCATIONS:
            if location in message_lower and location not in ['красная', 'поляна']:  # Исключаем отдельные слова
                # Нормализуем название
                if location == 'центр' or location == 'центральный':
                    found_locations.append('Центр')
                elif location == 'адлер' or location == 'адлерский':
                    found_locations.append('Адлер')
                elif location == 'сириус':
                    found_locations.append('Сириус')
                elif 'мор' in location or 'пляж' in location or 'побережье' in location:
                    found_locations.append('У моря')
                else:
                    found_locations.append(location.capitalize())
        
        # Добавляем уникальные локации
        for loc in found_locations:
            if loc not in lead.preferred_locations:
                lead.preferred_locations.append(loc)
    
    @classmethod
    def _extract_property_type(cls, message_lower: str, lead: LeadData):
        """Извлечение типа недвижимости"""
        for word, prop_type in cls.PROPERTY_TYPES.items():
            if word in message_lower:
                lead.property_type = prop_type
                break
    
    @classmethod
    def _extract_mortgage_bank(cls, message_lower: str, lead: LeadData):
        """Извлечение банка для ипотеки"""
        # Список популярных банков
        banks = ['сбер', 'втб', 'альфа', 'тинькофф', 'газпром', 'россельхоз', 'дом.рф', 'райффайзен']
        
        for bank in banks:
            if bank in message_lower:
                lead.mortgage_bank = bank.upper() if len(bank) <= 3 else bank.capitalize()
                break
        
        # Проверяем, оформлена ли ипотека
        if any(word in message_lower for word in ['оформлена', 'одобрена', 'есть одобрение']):
            lead.comments += ' Ипотека уже оформлена/одобрена.'


class DialogStateExtractor:
    """Экстрактор состояния диалога"""
    
    # Паттерны для определения состояний (НЕДВИЖИМОСТЬ СОЧИ)
    STATE_PATTERNS = {
        DialogState.S0_GREETING: [
            'привет', 'здравствуйте', 'добрый', 'начать', 'старт', 'продолжим'
        ],
        DialogState.S1_BUSINESS: [
            'сочи', 'в сочи', 'из', 'город', 'откуда', 'местный', 'прилечу', 'прилетаю'
        ],
        DialogState.S2_GOAL: [
            'инвестиции', 'инвестицию', 'пмж', 'проживание', 'переезд', 'аренд', 'сдавать', 'сбережения'
        ],
        DialogState.S3_PAYMENT: [
            'оплата', 'ипотека', 'наличные', 'рассрочка', 'кредит', 'банк'
        ],
        DialogState.S4_REQUIREMENTS: [
            'красная поляна', 'сириус', 'адлер', 'центр', 'локация', 'район', 'у моря'
        ],
        DialogState.S5_BUDGET: [
            'рублей', 'долларов', 'тысяч', 'млн', 'бюджет', 'до', 'от', 'стоимость'
        ],
        DialogState.S6_URGENCY: [
            'завтра', 'послезавтра', 'на неделе', 'срочно', 'быстро', 'когда', 'приезжаю'
        ],
        DialogState.S7_EXPERIENCE: [
            'видел', 'покупал', 'знаю', 'опыт', 'раньше', 'первый раз', 'в сочи'
        ],
        DialogState.S8_ACTION: [
            'показ', 'демо', 'встреча', 'звонок', 'готов', 'договариваемся', 'онлайн'
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
        """Определяет следующее состояние для НЕДВИЖИМОСТИ СОЧИ"""
        
        # Логика для недвижимости Сочи по инструкции
        if current_state == DialogState.S0_GREETING:
            # Если ответил на "для себя/инвестиции" или упомянул город - переходим к локации
            if any(word in message for word in ['инвестиц', 'пмж', 'себя', 'проживан', 'из ', 'сочи']):
                return DialogState.S1_BUSINESS
            return DialogState.S0_GREETING
        
        elif current_state == DialogState.S1_BUSINESS:
            # Если указал город или где находится - переходим к цели
            if lead.city or lead.is_in_sochi is not None:
                return DialogState.S2_GOAL
            if any(word in message for word in cls.STATE_PATTERNS[DialogState.S2_GOAL]):
                return DialogState.S2_GOAL
            return DialogState.S1_BUSINESS
        
        elif current_state == DialogState.S2_GOAL:
            # Если цель покупки определена - переходим к оплате
            if lead.automation_goal:
                return DialogState.S3_PAYMENT
            return DialogState.S2_GOAL
        
        elif current_state == DialogState.S3_PAYMENT:
            # Если способ оплаты определен - переходим к локации/требованиям
            if lead.payment_type or any(word in message for word in ['ипотек', 'наличн', 'рассроч']):
                return DialogState.S4_REQUIREMENTS
            return DialogState.S3_PAYMENT
        
        elif current_state == DialogState.S4_REQUIREMENTS:
            # Если локация определена - переходим к бюджету
            if lead.preferred_locations or any(word in message for word in ['красная', 'сириус', 'адлер', 'дом', 'квартир']):
                return DialogState.S5_BUDGET
            return DialogState.S4_REQUIREMENTS
        
        elif current_state == DialogState.S5_BUDGET:
            # Если бюджет определен - переходим к срочности
            if lead.budget_min or lead.budget_max:
                return DialogState.S6_URGENCY
            return DialogState.S5_BUDGET
        
        elif current_state == DialogState.S6_URGENCY:
            # Если срочность определена - переходим к опыту или действию
            if lead.urgency_date or lead.urgency_level:
                return DialogState.S7_EXPERIENCE
            return DialogState.S6_URGENCY
        
        elif current_state == DialogState.S7_EXPERIENCE:
            # После опыта - переходим к действию (показ/встреча)
            if any(word in message for word in cls.STATE_PATTERNS[DialogState.S8_ACTION]):
                return DialogState.S8_ACTION
            # Если опыт определен - можем переходить к действию
            if lead.sochi_experience:
                return DialogState.S8_ACTION
            return DialogState.S7_EXPERIENCE
        
        elif current_state == DialogState.S8_ACTION:
            # Остаемся в состоянии действия/показа
            return DialogState.S8_ACTION
        
        # По умолчанию остаемся в текущем состоянии
        return current_state
    
    @classmethod
    def calculate_qualification_status(cls, lead: LeadData) -> ClientType:
        """Вычисляет статус квалификации для НЕДВИЖИМОСТИ: Деньги + Срочность + Понимание запроса"""
        score = 0
        
        # Деньги (бюджет определен или способ оплаты)
        if lead.budget_min or lead.budget_max or lead.payment_type:
            score += 1
        
        # Срочность (готов быстро или указал дату приезда)
        if lead.urgency_date or lead.ready_for_quick_decision or lead.urgency_level in ['high', 'medium']:
            score += 1
        
        # Понимание запроса (цель покупки + тип недвижимости + локация)
        if lead.automation_goal and (lead.property_type or lead.preferred_locations):
            score += 1
        
        # Определяем тип клиента
        if score == 3:
            return ClientType.HOT     # 3 из 3 критериев
        elif score == 2:
            return ClientType.WARM    # 2 из 3 критериев
        else:
            return ClientType.COLD    # 1 из 3 критериев