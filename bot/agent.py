import json
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any

import openai
import anthropic
from zep_cloud.client import AsyncZep
from zep_cloud.types import Message

from .config import (
    INSTRUCTION_FILE, OPENAI_API_KEY, OPENAI_MODEL, ZEP_API_KEY, ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
    OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS, OPENAI_PRESENCE_PENALTY, OPENAI_FREQUENCY_PENALTY, OPENAI_TOP_P,
    ANTHROPIC_TEMPERATURE, ANTHROPIC_MAX_TOKENS, GOOGLE_SHEETS_ENABLED, GOOGLE_SHEETS_SYNC_INTERVAL
)
from .memory import MemoryService, DialogState, ClientType

# Настройка логирования
logger = logging.getLogger(__name__)


class AlenaAgent:
    """AI-ассистент Алёна с интеллектуальной системой памяти"""
    
    def __init__(self):
        # Инициализируем OpenAI клиент если API ключ доступен
        if OPENAI_API_KEY:
            self.openai_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
            print("✅ OpenAI клиент инициализирован")
        else:
            self.openai_client = None
            print("⚠️ OpenAI API ключ не найден")
        
        # Инициализируем Anthropic клиент если API ключ доступен
        if ANTHROPIC_API_KEY:
            try:
                self.anthropic_client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
                print("✅ Anthropic клиент инициализирован")
            except Exception as e:
                print(f"❌ Ошибка инициализации Anthropic: {e}")
                self.anthropic_client = None
        else:
            self.anthropic_client = None
            print("⚠️ Anthropic API ключ не найден")
            
        # Проверяем что хотя бы один LLM доступен
        if not self.openai_client and not self.anthropic_client:
            print("⚠️ Ни один LLM не доступен, используется упрощенный режим")
        
        # Инициализируем интеллектуальную систему памяти
        enable_memory = bool(ZEP_API_KEY and ZEP_API_KEY != "test_key")
        self.memory_service = MemoryService(ZEP_API_KEY or "", enable_memory=enable_memory)
        
        if enable_memory:
            print(f"✅ Интеллектуальная система памяти активирована")
            print(f"🧠 ZEP API Key: {ZEP_API_KEY[:8]}...{ZEP_API_KEY[-4:]}")
        else:
            print("⚠️ Система памяти работает в базовом режиме (без ZEP)")
        
        # Инициализируем Zep клиент для совместимости
        self.zep_client = self.memory_service.zep_client
        
        # Инициализируем Google Sheets интеграцию
        self.sheets_service = None
        if GOOGLE_SHEETS_ENABLED and enable_memory:
            try:
                from .integrations.google_sheets_service import GoogleSheetsService
                self.sheets_service = GoogleSheetsService(
                    self.memory_service, 
                    self.memory_service.analytics_service
                )
                print("✅ Google Sheets интеграция инициализирована")
            except Exception as e:
                print(f"⚠️ Ошибка инициализации Google Sheets: {e}")
                self.sheets_service = None
        elif GOOGLE_SHEETS_ENABLED:
            print("⚠️ Google Sheets требует активной системы памяти ZEP")
        
        self.instruction = self._load_instruction()
        self.user_sessions = {}  # Резервное хранение сессий в памяти
    
    def _load_instruction(self) -> Dict[str, Any]:
        try:
            with open(INSTRUCTION_FILE, 'r', encoding='utf-8') as f:
                instruction = json.load(f)
                logger.info(f"✅ Инструкции успешно загружены из {INSTRUCTION_FILE}")
                logger.info(f"📝 Последнее обновление: {instruction.get('last_updated', 'неизвестно')}")
                logger.info(f"📏 Длина системной инструкции: {len(instruction.get('system_instruction', ''))}")
                print(f"✅ Инструкции успешно загружены из {INSTRUCTION_FILE}")
                print(f"📝 Последнее обновление: {instruction.get('last_updated', 'неизвестно')}")
                return instruction
        except FileNotFoundError:
            logger.warning(f"⚠️ ВНИМАНИЕ: Файл {INSTRUCTION_FILE} не найден! Используется базовая инструкция.")
            print(f"⚠️ ВНИМАНИЕ: Файл {INSTRUCTION_FILE} не найден! Используется базовая инструкция.")
            return {
                "system_instruction": "Вы - помощник службы поддержки Textil PRO.",
                "welcome_message": "Добро пожаловать! Чем могу помочь?",
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Ошибка при загрузке инструкций: {e}")
            return {
                "system_instruction": "Вы - помощник службы поддержки Textil PRO.",
                "welcome_message": "Добро пожаловать! Чем могу помочь?",
                "last_updated": datetime.now().isoformat()
            }
    
    def reload_instruction(self):
        logger.info("🔄 Перезагрузка инструкций...")
        print("🔄 Перезагрузка инструкций...")
        old_updated = self.instruction.get('last_updated', 'неизвестно')
        self.instruction = self._load_instruction()
        new_updated = self.instruction.get('last_updated', 'неизвестно')
        
        if old_updated != new_updated:
            logger.info(f"✅ Инструкции обновлены: {old_updated} -> {new_updated}")
            print(f"✅ Инструкции обновлены: {old_updated} -> {new_updated}")
        else:
            logger.info("📝 Инструкции перезагружены (без изменений)")
            print("📝 Инструкции перезагружены (без изменений)")
    
    async def add_to_zep_memory(self, session_id: str, user_message: str, bot_response: str, user_name: str = None):
        """Добавляет сообщения в Zep Memory с именами пользователей"""
        if not self.zep_client:
            print(f"⚠️ Zep клиент не инициализирован, используем локальную память для {session_id}")
            self.add_to_local_session(session_id, user_message, bot_response)
            return False
            
        try:
            # Используем имя пользователя или ID для роли
            user_role = user_name if user_name else f"User_{session_id.split('_')[-1][:6]}"
            
            messages = [
                Message(
                    role=user_role,  # Имя пользователя вместо generic "user"
                    role_type="user",
                    content=user_message
                ),
                Message(
                    role="Анастасия",  # Имя бота-консультанта
                    role_type="assistant",
                    content=bot_response
                )
            ]
            
            await self.zep_client.memory.add(session_id=session_id, messages=messages)
            print(f"✅ Сообщения добавлены в Zep Cloud для сессии {session_id}")
            print(f"   📝 User: {user_message[:50]}...")
            print(f"   🤖 Bot: {bot_response[:50]}...")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при добавлении в Zep: {type(e).__name__}: {e}")
            # Fallback: добавляем в локальную память
            self.add_to_local_session(session_id, user_message, bot_response)
            return False
    
    async def get_zep_memory_context(self, session_id: str) -> str:
        """Получает контекст из Zep Memory"""
        if not self.zep_client:
            print(f"⚠️ Zep не доступен, используем локальную историю для {session_id}")
            return self.get_local_session_history(session_id)
            
        try:
            memory = await self.zep_client.memory.get(session_id=session_id)
            context = memory.context if memory.context else ""
            print(f"✅ Получен контекст из Zep для сессии {session_id}, длина: {len(context)}")
            return context
            
        except Exception as e:
            print(f"❌ Ошибка при получении контекста из Zep: {type(e).__name__}: {e}")
            return self.get_local_session_history(session_id)
    
    async def get_zep_recent_messages(self, session_id: str, limit: int = 6) -> str:
        """Получает последние сообщения из Zep Memory"""
        try:
            memory = await self.zep_client.memory.get(session_id=session_id)
            if not memory.messages:
                return ""
            
            recent_messages = memory.messages[-limit:]
            formatted_messages = []
            
            for msg in recent_messages:
                role = "Пользователь" if msg.role_type == "user" else "Ассистент"
                formatted_messages.append(f"{role}: {msg.content}")
            
            return "\n".join(formatted_messages)
            
        except Exception as e:
            print(f"❌ Ошибка при получении сообщений из Zep: {e}")
            return self.get_local_session_history(session_id)
    
    def add_to_local_session(self, session_id: str, user_message: str, bot_response: str):
        """Резервное локальное хранение сессий"""
        if session_id not in self.user_sessions:
            self.user_sessions[session_id] = []
        
        self.user_sessions[session_id].append({
            "user": user_message,
            "assistant": bot_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Ограничиваем историю 10 последними сообщениями
        if len(self.user_sessions[session_id]) > 10:
            self.user_sessions[session_id] = self.user_sessions[session_id][-10:]
    
    def get_local_session_history(self, session_id: str) -> str:
        """Получает историю из локального хранилища"""
        if session_id not in self.user_sessions:
            return ""
        
        history = []
        for exchange in self.user_sessions[session_id][-6:]:  # Последние 6 обменов
            history.append(f"Пользователь: {exchange['user']}")
            history.append(f"Ассистент: {exchange['assistant']}")
        
        return "\n".join(history) if history else ""
    
    async def call_llm(self, messages: list, max_tokens: int = None, temperature: float = None) -> str:
        """Роутер LLM запросов с fallback между OpenAI и Anthropic (с параметрами для живого общения)"""
        
        # Используем конфигурационные значения если не переданы
        max_tokens = max_tokens or OPENAI_MAX_TOKENS
        temperature = temperature or OPENAI_TEMPERATURE
        
        # Сначала пробуем OpenAI
        if self.openai_client:
            try:
                logger.info(f"🤖 OpenAI запрос: temp={temperature}, tokens={max_tokens}, presence={OPENAI_PRESENCE_PENALTY}, frequency={OPENAI_FREQUENCY_PENALTY}")
                response = await self.openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    presence_penalty=OPENAI_PRESENCE_PENALTY,
                    frequency_penalty=OPENAI_FREQUENCY_PENALTY,
                    top_p=OPENAI_TOP_P
                )
                result = response.choices[0].message.content
                logger.info("✅ OpenAI ответ получен с расширенными параметрами")
                return result
                
            except Exception as e:
                logger.error(f"❌ Ошибка OpenAI: {e}")
                print(f"❌ OpenAI недоступен: {e}")
        
        # Fallback на Anthropic
        if self.anthropic_client:
            try:
                # Используем параметры Anthropic если OpenAI недоступен
                anthropic_max_tokens = max_tokens or ANTHROPIC_MAX_TOKENS
                anthropic_temperature = temperature or ANTHROPIC_TEMPERATURE
                
                logger.info(f"🤖 Fallback на Anthropic: temp={anthropic_temperature}, tokens={anthropic_max_tokens}")
                
                # Конвертируем сообщения для Anthropic API
                system_message = ""
                user_messages = []
                
                for msg in messages:
                    if msg["role"] == "system":
                        system_message = msg["content"]
                    else:
                        user_messages.append(msg)
                
                response = await self.anthropic_client.messages.create(
                    model=ANTHROPIC_MODEL,
                    max_tokens=anthropic_max_tokens,
                    temperature=anthropic_temperature,
                    system=system_message,
                    messages=user_messages
                )
                
                result = response.content[0].text
                logger.info("✅ Anthropic ответ получен")
                return result
                
            except Exception as e:
                logger.error(f"❌ Ошибка Anthropic: {e}")
                print(f"❌ Anthropic недоступен: {e}")
        
        # Если оба LLM недоступны - используем fallback логику
        logger.warning("❌ Все LLM недоступны, используем локальную логику")
        return self._fallback_response(messages[-1]["content"] if messages else "")
    
    def _fallback_response(self, user_message: str) -> str:
        """Fallback ответы когда LLM недоступны - выбрасываем ошибку"""
        raise Exception("LLM недоступен, fallback ответы отключены")
    
    async def generate_response(self, user_message: str, session_id: str, user_name: str = None) -> str:
        try:
            # 🧠 ИНТЕЛЛЕКТУАЛЬНАЯ ОБРАБОТКА СООБЩЕНИЯ
            memory_result = await self.memory_service.process_message(
                user_id=session_id, 
                message_text=user_message
            )
            
            if not memory_result.get('success', False):
                logger.error(f"❌ Ошибка системы памяти: {memory_result.get('error')}")
                # Продолжаем с базовой логикой
            
            # Получаем данные о клиенте и состоянии диалога
            lead_data = memory_result.get('lead_data')
            current_state = memory_result.get('current_state', DialogState.S0_GREETING)
            qualification_status = memory_result.get('qualification_status', ClientType.COLD)
            recommendations = memory_result.get('recommendations', {})
            should_escalate = memory_result.get('should_escalate', False)
            
            # Формируем улучшенный системный промпт с контекстом
            system_prompt = self._build_contextual_system_prompt(
                lead_data, current_state, qualification_status, recommendations
            )
            
            # Получаем историю диалога
            dialog_history = await self.memory_service.get_dialog_history(session_id, limit=5)
            
            # Формируем сообщения для LLM
            messages = self._build_llm_messages(
                system_prompt, user_message, dialog_history, recommendations
            )
            
            # Генерируем ответ через LLM
            if self.openai_client or self.anthropic_client:
                try:
                    bot_response = await self.call_llm(messages)
                except Exception as llm_error:
                    logger.error(f"❌ Ошибка LLM роутера: {llm_error}")
                    bot_response = self._fallback_response_with_context(
                        user_message, current_state, recommendations
                    )
            else:
                bot_response = self._fallback_response_with_context(
                    user_message, current_state, recommendations
                )
            
            # 🚨 ПРОВЕРКА НА ЭСКАЛАЦИЮ
            if should_escalate:
                escalation_note = self._generate_escalation_summary(lead_data)
                logger.info(f"🔥 ЭСКАЛАЦИЯ для {session_id}: {escalation_note}")
                print(f"🔥 ГОРЯЧИЙ ЛИД: {session_id} - {escalation_note}")
            
            # Сохраняем ответ в память
            await self.memory_service.process_message(
                user_id=session_id,
                message_text=bot_response,
                message_type="assistant"
            )
            
            # Совместимость: сохраняем также в старую систему памяти
            await self.add_to_zep_memory(session_id, user_message, bot_response, user_name)
            
            # Синхронизация с Google Sheets при значимых изменениях
            if self.sheets_service and lead_data:
                try:
                    # Проверяем, есть ли значимые изменения в данных лида
                    significant_changes = (
                        should_escalate or 
                        qualification_status in [ClientType.WARM, ClientType.HOT] or
                        current_state in [DialogState.S3_PAYMENT, DialogState.S5_BUDGET, DialogState.S8_ACTION]
                    )
                    
                    if significant_changes:
                        # Асинхронная синхронизация без блокировки ответа
                        asyncio.create_task(self._sync_to_sheets_async(session_id))
                        logger.debug(f"📊 Запущена синхронизация с Google Sheets для {session_id}")
                        
                except Exception as sheets_error:
                    logger.error(f"❌ Ошибка синхронизации Google Sheets: {sheets_error}")
            
            return bot_response
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка генерации ответа для {session_id}: {e}")
            return self._emergency_fallback_response(user_message)
    
    def _build_contextual_system_prompt(self, lead_data, current_state: DialogState, 
                                      qualification_status: ClientType, 
                                      recommendations: Dict[str, Any]) -> str:
        """Строит контекстуальный системный промпт"""
        base_prompt = self.instruction.get("system_instruction", "")
        
        # Добавляем контекст о клиенте
        context_parts = []
        
        if lead_data:
            client_info = []
            if lead_data.name:
                client_info.append(f"Имя: {lead_data.name}")
            if lead_data.business_sphere:
                client_info.append(f"Сфера: {lead_data.business_sphere}")
            if lead_data.automation_goal:
                client_info.append(f"Цель: {lead_data.automation_goal.value}")
            if lead_data.budget_min or lead_data.budget_max:
                budget = f"Бюджет: ${lead_data.budget_min or 0}-{lead_data.budget_max or '∞'}"
                client_info.append(budget)
            
            if client_info:
                context_parts.append(f"ДАННЫЕ КЛИЕНТА: {' | '.join(client_info)}")
        
        # Добавляем состояние диалога (недвижимость Сочи)
        state_descriptions = {
            DialogState.S0_GREETING: "Первое знакомство - выясните цель покупки",
            DialogState.S1_BUSINESS: "Узнайте местоположение клиента и город", 
            DialogState.S2_GOAL: "Определите цель покупки недвижимости",
            DialogState.S3_PAYMENT: "Обсудите форму оплаты и бюджет",
            DialogState.S4_REQUIREMENTS: "Выясните требования к объекту",
            DialogState.S5_BUDGET: "Уточните бюджет через примеры",
            DialogState.S6_URGENCY: "Определите срочность покупки",
            DialogState.S7_EXPERIENCE: "Узнайте опыт покупки в Сочи",
            DialogState.S8_ACTION: "Предложите онлайн-показ или встречу"
        }
        
        state_desc = state_descriptions.get(current_state, "")
        context_parts.append(f"ЭТАП ДИАЛОГА: {current_state.value} - {state_desc}")
        
        # Добавляем статус квалификации
        status_descriptions = {
            ClientType.COLD: "ХОЛОДНЫЙ - нужна базовая информация о потребностях",
            ClientType.WARM: "ТЁПЛЫЙ - есть интерес, развивайте диалог", 
            ClientType.HOT: "ГОРЯЧИЙ - готов к покупке, предлагайте онлайн-показ!"
        }
        
        status_desc = status_descriptions.get(qualification_status, "")
        context_parts.append(f"СТАТУС КЛИЕНТА: {status_desc}")
        
        # Добавляем рекомендации
        if recommendations.get('next_questions'):
            questions = recommendations['next_questions'][:2]  # Максимум 2 вопроса
            context_parts.append(f"РЕКОМЕНДУЕМЫЕ ВОПРОСЫ: {' | '.join(questions)}")
        
        if recommendations.get('demo_ready'):
            context_parts.append("🎯 ГОТОВ К ПОКАЗУ: Предложите конкретные слоты для онлайн-показа!")
        
        # Объединяем все части
        if context_parts:
            base_prompt += f"\n\n{'='*50}\n" + "\n".join(context_parts) + f"\n{'='*50}"
        
        return base_prompt
    
    def _build_llm_messages(self, system_prompt: str, user_message: str, 
                           dialog_history: list, recommendations: Dict[str, Any]) -> list:
        """Строит сообщения для LLM с учетом истории"""
        messages = [{"role": "system", "content": system_prompt}]
        
        # Добавляем краткую историю если есть
        if dialog_history:
            history_text = "НЕДАВНИЕ СООБЩЕНИЯ:\n"
            for msg in dialog_history[-3:]:  # Последние 3 сообщения
                role = "👤 Клиент" if msg['role'] == 'user' else "🤖 Алёна"
                content = msg['content'][:200] if len(msg['content']) > 200 else msg['content']
                history_text += f"{role}: {content}\n"
            
            messages.append({"role": "system", "content": history_text})
        
        # Текущее сообщение пользователя
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _fallback_response_with_context(self, user_message: str, current_state: DialogState, 
                                      recommendations: Dict[str, Any]) -> str:
        """Fallback ответ с учетом контекста диалога - выбрасываем ошибку"""
        raise Exception("LLM недоступен, fallback ответы с контекстом отключены")
    
    def _emergency_fallback_response(self, user_message: str) -> str:
        """Аварийный ответ при полном отказе систем - выбрасываем ошибку"""
        raise Exception("Критическая ошибка: все системы недоступны, аварийные fallback отключены")
    
    def _generate_escalation_summary(self, lead_data) -> str:
        """Генерирует сводку для эскалации"""
        if not lead_data:
            return "Горячий лид без данных"
        
        summary_parts = []
        
        if lead_data.name:
            summary_parts.append(f"Имя: {lead_data.name}")
        if lead_data.phone:
            summary_parts.append(f"Телефон: {lead_data.phone}")
        if lead_data.business_sphere:
            summary_parts.append(f"Сфера: {lead_data.business_sphere}")
        if lead_data.budget_max:
            summary_parts.append(f"Бюджет: до ${lead_data.budget_max}")
        if lead_data.automation_goal:
            summary_parts.append(f"Цель: {lead_data.automation_goal.value}")
        
        return " | ".join(summary_parts) if summary_parts else "Горячий лид - требует внимания"
    
    # Новые методы для работы с системой памяти
    async def get_lead_analytics(self, session_id: str) -> Dict[str, Any]:
        """Получает аналитику по лиду"""
        return await self.memory_service.get_analytics_summary(session_id)
    
    async def get_memory_insights(self, session_id: str) -> Dict[str, Any]:
        """Получает инсайты из системы памяти"""
        try:
            lead_data = await self.memory_service.get_lead_data(session_id)
            dialog_history = await self.memory_service.get_dialog_history(session_id, limit=20)
            
            return {
                'lead_data': lead_data.to_dict() if lead_data else {},
                'dialog_history': dialog_history,
                'current_state': lead_data.current_dialog_state.value if lead_data else 's0_greeting',
                'qualification_status': lead_data.qualification_status.value if lead_data and lead_data.qualification_status else 'cold',
                'should_escalate': self.memory_service._should_escalate(lead_data) if lead_data else False
            }
        except Exception as e:
            logger.error(f"❌ Ошибка получения инсайтов памяти для {session_id}: {e}")
            return {}
    
    async def process_reminder_due(self, session_id: str) -> Optional[str]:
        """Обрабатывает готовые напоминания"""
        try:
            due_reminders = await self.memory_service.reminders.get_due_reminders()
            session_reminders = [r for r in due_reminders if r.session_id == session_id]
            
            if session_reminders:
                reminder = session_reminders[0]  # Берем первое
                lead_data = await self.memory_service.get_lead_data(session_id)
                
                # Генерируем сообщение напоминания
                message = await self.memory_service.reminders.generate_reminder_message(
                    reminder, lead_data.to_dict() if lead_data else None
                )
                
                # Помечаем как выполненное
                await self.memory_service.reminders.mark_reminder_completed(reminder)
                
                return message
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки напоминания для {session_id}: {e}")
            return None
    
    async def ensure_user_exists(self, user_id: str, user_data: Dict[str, Any] = None):
        """Создает пользователя в Zep если его еще нет"""
        if not self.zep_client:
            return False
            
        try:
            # Пытаемся получить пользователя
            try:
                user = await self.zep_client.user.get(user_id=user_id)
                print(f"✅ Пользователь {user_id} уже существует в Zep")
                return True
            except:
                # Пользователь не существует, создаем
                pass
            
            # Создаем нового пользователя
            user_info = user_data or {}
            await self.zep_client.user.add(
                user_id=user_id,
                first_name=user_info.get('first_name', 'User'),
                last_name=user_info.get('last_name', ''),
                email=user_info.get('email', f'{user_id}@telegram.user'),
                metadata={
                    'source': 'telegram',
                    'created_at': datetime.now().isoformat()
                }
            )
            print(f"✅ Создан новый пользователь в Zep: {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при создании пользователя в Zep: {e}")
            return False
    
    async def ensure_session_exists(self, session_id: str, user_id: str):
        """Создает сессию в Zep если ее еще нет"""
        if not self.zep_client:
            return False
            
        try:
            # Создаем сессию
            await self.zep_client.memory.add_session(
                session_id=session_id,
                user_id=user_id,
                metadata={
                    'channel': 'telegram',
                    'created_at': datetime.now().isoformat()
                }
            )
            print(f"✅ Создана сессия в Zep: {session_id} для пользователя {user_id}")
            return True
            
        except Exception as e:
            # Сессия может уже существовать или будет создана автоматически
            print(f"ℹ️ Сессия {session_id} возможно уже существует или будет создана автоматически")
            return True
    
    async def _sync_to_sheets_async(self, session_id: str):
        """Асинхронная синхронизация данных с Google Sheets"""
        if not self.sheets_service:
            return
            
        try:
            logger.debug(f"📊 Начинаю синхронизацию Google Sheets для сессии {session_id}")
            
            # Аутентификация если нужно
            if not self.sheets_service._authenticated:
                auth_success = await self.sheets_service.authenticate()
                if not auth_success:
                    logger.error("❌ Не удалось аутентифицироваться в Google Sheets")
                    return
            
            # Создание таблицы если не создана
            if not self.sheets_service.spreadsheet_id:
                spreadsheet_id = await self.sheets_service.create_spreadsheet()
                if not spreadsheet_id:
                    logger.error("❌ Не удалось создать Google таблицу")
                    return
                logger.info(f"📊 Создана новая Google таблица: {spreadsheet_id}")
            
            # Синхронизация данных лидов
            leads_success = await self.sheets_service.sync_leads_data(days=30)
            if leads_success:
                logger.debug(f"✅ Данные лидов синхронизированы для {session_id}")
            
            # Синхронизация аналитики
            analytics_success = await self.sheets_service.sync_analytics_data(days=30)
            if analytics_success:
                logger.debug(f"✅ Аналитика синхронизирована для {session_id}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка асинхронной синхронизации Google Sheets: {e}")
    
    async def setup_google_sheets_periodic_sync(self):
        """Запускает периодическую синхронизацию Google Sheets"""
        if not self.sheets_service or not GOOGLE_SHEETS_ENABLED:
            return
            
        try:
            logger.info("🔄 Запуск периодической синхронизации Google Sheets")
            await self.sheets_service.setup_periodic_sync(GOOGLE_SHEETS_SYNC_INTERVAL)
        except Exception as e:
            logger.error(f"❌ Ошибка периодической синхронизации Google Sheets: {e}")
    
    async def get_sheets_url(self) -> Optional[str]:
        """Возвращает URL Google таблицы если она создана"""
        if self.sheets_service:
            return await self.sheets_service.get_spreadsheet_url()
        return None
    
    async def manual_sheets_sync(self) -> bool:
        """Ручная синхронизация данных с Google Sheets"""
        if not self.sheets_service:
            logger.warning("⚠️ Google Sheets сервис не инициализирован")
            return False
            
        try:
            # Аутентификация
            if not self.sheets_service._authenticated:
                auth_success = await self.sheets_service.authenticate()
                if not auth_success:
                    return False
            
            # Создание таблицы если нужно
            if not self.sheets_service.spreadsheet_id:
                spreadsheet_id = await self.sheets_service.create_spreadsheet()
                if not spreadsheet_id:
                    return False
            
            # Синхронизация
            leads_success = await self.sheets_service.sync_leads_data(days=30)
            analytics_success = await self.sheets_service.sync_analytics_data(days=30)
            
            if leads_success and analytics_success:
                logger.info("✅ Ручная синхронизация Google Sheets завершена успешно")
                return True
            else:
                logger.warning("⚠️ Ручная синхронизация Google Sheets завершена с ошибками")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка ручной синхронизации Google Sheets: {e}")
            return False

    def get_welcome_message(self) -> str:
        return self.instruction.get("welcome_message", "Добро пожаловать!")


agent = AlenaAgent()