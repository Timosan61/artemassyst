"""
Сервис аналитики для системы памяти
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

from .models import AnalyticsData

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Сервис для сбора и анализа данных о работе системы памяти"""
    
    def __init__(self, storage_path: str = "data/analytics"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Файлы для хранения данных
        self.events_file = self.storage_path / "events.jsonl"
        self.daily_stats_file = self.storage_path / "daily_stats.json"
        
    async def track_event(self, session_id: str, event_type: str, 
                         event_data: Dict[str, Any] = None):
        """Отслеживает событие в аналитике"""
        try:
            event = AnalyticsData(
                session_id=session_id,
                event_type=event_type,
                event_data=event_data or {}
            )
            
            # Сохраняем событие
            await self._save_event(event)
            
            # Обновляем статистику
            await self._update_daily_stats(event)
            
            logger.debug(f"📊 Событие отслежено: {event_type} для {session_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка отслеживания события: {e}")
    
    async def get_session_events(self, session_id: str, 
                               days: int = 7) -> List[Dict[str, Any]]:
        """Получает события для конкретной сессии"""
        try:
            events = []
            cutoff_date = datetime.now() - timedelta(days=days)
            
            if not self.events_file.exists():
                return events
            
            with open(self.events_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        event_data = json.loads(line.strip())
                        event_time = datetime.fromisoformat(event_data['timestamp'])
                        
                        if (event_data['session_id'] == session_id and 
                            event_time >= cutoff_date):
                            events.append(event_data)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
            
            # Сортируем по времени
            events.sort(key=lambda x: x['timestamp'])
            return events
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения событий для {session_id}: {e}")
            return []
    
    async def get_conversion_funnel(self, days: int = 30) -> Dict[str, Any]:
        """Анализирует воронку конверсии"""
        try:
            funnel_data = {
                's0_greeting': 0,
                's1_business': 0, 
                's2_goal': 0,
                's3_payment': 0,
                's4_requirements': 0,
                's5_budget': 0,
                's6_urgency': 0,
                's7_experience': 0,
                's8_action': 0,
                'qualification_cold': 0,
                'qualification_warm': 0,
                'qualification_hot': 0,
                'escalations': 0
            }
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            if not self.events_file.exists():
                return funnel_data
            
            # Анализируем события
            with open(self.events_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        event_data = json.loads(line.strip())
                        event_time = datetime.fromisoformat(event_data['timestamp'])
                        
                        if event_time < cutoff_date:
                            continue
                        
                        event_type = event_data['event_type']
                        
                        # Состояния диалога
                        if event_type == 'state_change':
                            to_state = event_data['event_data'].get('to', '')
                            if to_state in funnel_data:
                                funnel_data[to_state] += 1
                        
                        # Статусы квалификации
                        elif event_type == 'qualification_change':
                            status = event_data['event_data'].get('status', '')
                            key = f'qualification_{status}'
                            if key in funnel_data:
                                funnel_data[key] += 1
                        
                        # Эскалации
                        elif event_type == 'escalation':
                            funnel_data['escalations'] += 1
                            
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
            
            # Вычисляем конверсию
            total_sessions = funnel_data['s0_greeting'] or 1
            conversion_rates = {}
            
            for key, value in funnel_data.items():
                if key.startswith('s') and key != 's0_greeting':
                    conversion_rates[key] = (value / total_sessions) * 100
            
            return {
                'funnel_data': funnel_data,
                'conversion_rates': conversion_rates,
                'total_sessions': total_sessions,
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа воронки: {e}")
            return {}
    
    async def get_daily_stats(self, days: int = 30) -> List[Dict[str, Any]]:
        """Получает ежедневную статистику"""
        try:
            if not self.daily_stats_file.exists():
                return []
            
            with open(self.daily_stats_file, 'r', encoding='utf-8') as f:
                all_stats = json.load(f)
            
            # Фильтруем по дате
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered_stats = []
            
            for date_str, stats in all_stats.items():
                try:
                    stat_date = datetime.strptime(date_str, '%Y-%m-%d')
                    if stat_date >= cutoff_date:
                        stats['date'] = date_str
                        filtered_stats.append(stats)
                except ValueError:
                    continue
            
            # Сортируем по дате
            filtered_stats.sort(key=lambda x: x['date'])
            return filtered_stats
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения ежедневной статистики: {e}")
            return []
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Получает метрики производительности"""
        try:
            metrics = {
                'avg_response_time': 0.0,
                'successful_extractions': 0,
                'failed_extractions': 0,
                'memory_usage': 0,
                'escalation_rate': 0.0,
                'qualification_accuracy': 0.0
            }
            
            # Анализируем последние события
            recent_events = await self._get_recent_events(hours=24)
            
            total_events = len(recent_events)
            if total_events == 0:
                return metrics
            
            successful_ops = 0
            failed_ops = 0
            escalations = 0
            
            for event in recent_events:
                event_type = event.get('event_type', '')
                
                if event_type == 'extraction_success':
                    successful_ops += 1
                elif event_type == 'extraction_failed':
                    failed_ops += 1
                elif event_type == 'escalation':
                    escalations += 1
            
            # Вычисляем метрики
            metrics['successful_extractions'] = successful_ops
            metrics['failed_extractions'] = failed_ops
            metrics['escalation_rate'] = (escalations / total_events) * 100
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения метрик производительности: {e}")
            return {}
    
    async def generate_report(self, days: int = 7) -> Dict[str, Any]:
        """Генерирует сводный отчет"""
        try:
            report = {
                'period': f'Last {days} days',
                'generated_at': datetime.now().isoformat(),
                'summary': {},
                'funnel_analysis': {},
                'performance_metrics': {},
                'daily_trends': [],
                'recommendations': []
            }
            
            # Получаем данные
            funnel = await self.get_conversion_funnel(days)
            daily_stats = await self.get_daily_stats(days)
            performance = await self.get_performance_metrics()
            
            # Формируем отчет
            report['funnel_analysis'] = funnel
            report['performance_metrics'] = performance
            report['daily_trends'] = daily_stats
            
            # Сводка
            total_sessions = funnel.get('total_sessions', 0)
            hot_leads = funnel.get('funnel_data', {}).get('qualification_hot', 0)
            escalations = funnel.get('funnel_data', {}).get('escalations', 0)
            
            report['summary'] = {
                'total_sessions': total_sessions,
                'hot_leads': hot_leads,
                'hot_lead_rate': (hot_leads / max(total_sessions, 1)) * 100,
                'escalation_rate': (escalations / max(total_sessions, 1)) * 100
            }
            
            # Рекомендации
            report['recommendations'] = await self._generate_recommendations(report)
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации отчета: {e}")
            return {}
    
    async def _save_event(self, event: AnalyticsData):
        """Сохраняет событие в файл"""
        try:
            event_json = json.dumps(event.to_dict(), ensure_ascii=False)
            
            with open(self.events_file, 'a', encoding='utf-8') as f:
                f.write(event_json + '\n')
                
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения события: {e}")
    
    async def _update_daily_stats(self, event: AnalyticsData):
        \"\"\"Обновляет ежедневную статистику\"\"\"
        try:
            today = event.timestamp.strftime('%Y-%m-%d')
            
            # Загружаем существующую статистику
            daily_stats = {}
            if self.daily_stats_file.exists():
                with open(self.daily_stats_file, 'r', encoding='utf-8') as f:
                    daily_stats = json.load(f)
            
            # Инициализируем день если его нет
            if today not in daily_stats:
                daily_stats[today] = {
                    'total_events': 0,
                    'sessions': set(),
                    'event_types': {}
                }
            
            # Обновляем статистику
            day_stats = daily_stats[today]
            day_stats['total_events'] += 1
            
            # Добавляем сессию (используем set для уникальности)
            if isinstance(day_stats['sessions'], list):
                day_stats['sessions'] = set(day_stats['sessions'])
            day_stats['sessions'].add(event.session_id)
            
            # Считаем типы событий
            event_type = event.event_type
            if event_type not in day_stats['event_types']:
                day_stats['event_types'][event_type] = 0
            day_stats['event_types'][event_type] += 1
            
            # Конвертируем set обратно в list для JSON
            day_stats['sessions'] = list(day_stats['sessions'])
            day_stats['unique_sessions'] = len(day_stats['sessions'])
            
            # Сохраняем
            with open(self.daily_stats_file, 'w', encoding='utf-8') as f:
                json.dump(daily_stats, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления ежедневной статистики: {e}")
    
    async def _get_recent_events(self, hours: int = 24) -> List[Dict[str, Any]]:
        \"\"\"Получает события за последние часы\"\"\"
        try:
            events = []
            cutoff_date = datetime.now() - timedelta(hours=hours)
            
            if not self.events_file.exists():
                return events
            
            with open(self.events_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        event_data = json.loads(line.strip())
                        event_time = datetime.fromisoformat(event_data['timestamp'])
                        
                        if event_time >= cutoff_date:
                            events.append(event_data)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
            
            return events
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения недавних событий: {e}")
            return []
    
    async def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        \"\"\"Генерирует рекомендации на основе отчета\"\"\"
        recommendations = []
        
        try:
            summary = report.get('summary', {})
            funnel = report.get('funnel_analysis', {}).get('conversion_rates', {})
            
            # Анализируем конверсию
            hot_lead_rate = summary.get('hot_lead_rate', 0)
            escalation_rate = summary.get('escalation_rate', 0)
            
            if hot_lead_rate < 10:
                recommendations.append(
                    \"Низкая конверсия в горячие лиды. Рекомендуется улучшить квалификацию.\"
                )
            
            if escalation_rate < 20:
                recommendations.append(
                    \"Низкий уровень эскалации. Возможно, пропускаются готовые клиенты.\"
                )
            
            # Анализируем воронку
            if funnel.get('s2_goal', 0) < 50:
                recommendations.append(
                    \"Много клиентов не доходят до определения цели. Улучшите вопросы о потребностях.\"
                )
            
            if funnel.get('s5_budget', 0) < 30:
                recommendations.append(
                    \"Клиенты избегают обсуждения бюджета. Пересмотрите подход к выяснению бюджета.\"
                )
            
            if not recommendations:
                recommendations.append(\"Система работает эффективно. Продолжайте мониторинг.\")
            
            return recommendations
            
        except Exception as e:
            logger.error(f\"❌ Ошибка генерации рекомендаций: {e}\")
            return [\"Не удалось сгенерировать рекомендации\"]