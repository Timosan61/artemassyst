"""
Интеллектуальная система памяти для AI-ассистента "Алёна"
"""

from .models import (
    DialogState,
    ClientType,
    AutomationGoal,
    PaymentType,
    LeadData,
    ReminderTask,
    AnalyticsData
)

from .extractors import (
    LeadDataExtractor,
    DialogStateExtractor
)

from .memory_service import MemoryService
from .analytics import AnalyticsService
from .reminders import ReminderService
from .session_manager import SessionManager, session_manager

__all__ = [
    # Models
    'DialogState',
    'ClientType',
    'AutomationGoal',
    'PaymentType',
    'LeadData',
    'ReminderTask',
    'AnalyticsData',

    # Services
    'MemoryService',
    'AnalyticsService',
    'ReminderService',
    'SessionManager',
    'session_manager',

    # Extractors
    'LeadDataExtractor',
    'DialogStateExtractor'
]