#!/usr/bin/env python3
"""
Скрипт для анализа диалогов бота
Позволяет быстро просматривать и анализировать логи переписки
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import asyncio
from collections import defaultdict, Counter

# Добавляем путь для импорта модулей бота
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def load_dialog_logs(days_back: int = 7) -> List[Dict]:
    """Загрузка логов диалогов за последние N дней"""
    logs_dir = Path("logs/dialogs")
    if not logs_dir.exists():
        print("❌ Директория логов не найдена")
        return []

    messages = []
    cutoff_date = datetime.now() - timedelta(days=days_back)

    # Ищем файлы логов за указанный период
    for log_file in logs_dir.glob("dialogs_*.jsonl"):
        try:
            # Извлекаем дату из имени файла
            date_str = log_file.stem.replace("dialogs_", "")
            file_date = datetime.strptime(date_str, "%Y-%m-%d")

            if file_date >= cutoff_date:
                print(f"📂 Загрузка {log_file.name}...")
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                message = json.loads(line.strip())
                                messages.append(message)
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            print(f"⚠️ Ошибка загрузки {log_file}: {e}")

    return sorted(messages, key=lambda x: x.get('timestamp', ''))

def analyze_user_journey(messages: List[Dict], user_id: str = None) -> Dict:
    """Анализ пути пользователя через состояния диалога"""
    if user_id:
        user_messages = [m for m in messages if m.get('user_id') == user_id]
    else:
        user_messages = messages

    # Группируем по пользователям
    user_journeys = defaultdict(list)
    for msg in user_messages:
        if 'user_id' in msg and 'state' in msg:
            user_journeys[msg['user_id']].append({
                'timestamp': msg['timestamp'],
                'state': msg['state'],
                'message_type': msg['message_type'],
                'text': msg['text'][:100] + '...' if len(msg['text']) > 100 else msg['text']
            })

    return dict(user_journeys)

def analyze_state_transitions(messages: List[Dict]) -> Dict:
    """Анализ переходов между состояниями"""
    transitions = defaultdict(int)
    state_durations = defaultdict(list)
    user_states = defaultdict(list)

    for msg in messages:
        if 'user_id' in msg and 'state' in msg and msg.get('message_type') == 'user':
            user_id = msg['user_id']
            state = msg['state']
            timestamp = msg['timestamp']

            user_states[user_id].append({
                'state': state,
                'timestamp': timestamp
            })

    # Анализируем переходы для каждого пользователя
    for user_id, states in user_states.items():
        states.sort(key=lambda x: x['timestamp'])

        for i in range(1, len(states)):
            prev_state = states[i-1]['state']
            curr_state = states[i]['state']

            if prev_state != curr_state:
                transition_key = f"{prev_state} → {curr_state}"
                transitions[transition_key] += 1

                # Вычисляем длительность состояния
                try:
                    prev_time = datetime.fromisoformat(states[i-1]['timestamp'])
                    curr_time = datetime.fromisoformat(states[i]['timestamp'])
                    duration = (curr_time - prev_time).total_seconds()
                    state_durations[prev_state].append(duration)
                except:
                    continue

    return {
        'transitions': dict(transitions),
        'state_durations': {
            state: {
                'count': len(durations),
                'avg_duration': sum(durations) / len(durations) if durations else 0,
                'min_duration': min(durations) if durations else 0,
                'max_duration': max(durations) if durations else 0
            }
            for state, durations in state_durations.items()
        }
    }

def analyze_qualification_progress(messages: List[Dict]) -> Dict:
    """Анализ прогресса квалификации клиентов"""
    qualification_changes = defaultdict(list)

    for msg in messages:
        if 'user_id' in msg and 'qualification' in msg:
            user_id = msg['user_id']
            qualification = msg['qualification']
            timestamp = msg['timestamp']

            qualification_changes[user_id].append({
                'qualification': qualification,
                'timestamp': timestamp
            })

    # Анализируем изменения квалификации
    progression = {'COLD→WARM': 0, 'WARM→HOT': 0, 'COLD→HOT': 0}
    current_qualifications = Counter()

    for user_id, changes in qualification_changes.items():
        changes.sort(key=lambda x: x['timestamp'])

        if changes:
            # Текущая квалификация
            current_qualifications[changes[-1]['qualification']] += 1

            # Отслеживаем прогрессию
            qualifications = [c['qualification'] for c in changes]
            unique_qualifications = []

            # Убираем дубликаты, сохраняя порядок
            for q in qualifications:
                if not unique_qualifications or unique_qualifications[-1] != q:
                    unique_qualifications.append(q)

            # Анализируем переходы
            for i in range(1, len(unique_qualifications)):
                prev_qual = unique_qualifications[i-1]
                curr_qual = unique_qualifications[i]
                transition_key = f"{prev_qual}→{curr_qual}"
                if transition_key in progression:
                    progression[transition_key] += 1

    return {
        'current_qualifications': dict(current_qualifications),
        'progression': progression
    }

def find_problem_dialogs(messages: List[Dict]) -> List[Dict]:
    """Поиск проблемных диалогов (зацикленные состояния, повторные приветствия)"""
    problems = []
    user_dialogs = defaultdict(list)

    # Группируем сообщения по пользователям
    for msg in messages:
        if 'user_id' in msg:
            user_dialogs[msg['user_id']].append(msg)

    for user_id, user_messages in user_dialogs.items():
        user_messages.sort(key=lambda x: x.get('timestamp', ''))

        # Проверяем повторные приветствия
        greeting_count = 0
        s0_greetings = []

        for msg in user_messages:
            if (msg.get('message_type') == 'assistant' and
                msg.get('state') == 'S0_GREETING' and
                'Здравствуйте' in msg.get('text', '')):
                greeting_count += 1
                s0_greetings.append({
                    'timestamp': msg['timestamp'],
                    'text': msg['text'][:100] + '...'
                })

        if greeting_count > 1:
            problems.append({
                'user_id': user_id,
                'type': 'multiple_greetings',
                'count': greeting_count,
                'details': s0_greetings,
                'severity': 'high' if greeting_count > 3 else 'medium'
            })

        # Проверяем зацикленные состояния
        states_sequence = []
        for msg in user_messages:
            if msg.get('message_type') == 'user' and 'state' in msg:
                states_sequence.append(msg['state'])

        # Ищем повторения состояний подряд
        repeated_states = []
        current_state = None
        repeat_count = 0

        for state in states_sequence:
            if state == current_state:
                repeat_count += 1
            else:
                if repeat_count > 2:  # Более 2 повторений подряд
                    repeated_states.append({
                        'state': current_state,
                        'count': repeat_count
                    })
                current_state = state
                repeat_count = 1

        if repeated_states:
            problems.append({
                'user_id': user_id,
                'type': 'stuck_in_state',
                'details': repeated_states,
                'severity': 'high'
            })

    return problems

def generate_report(messages: List[Dict], output_file: str = None) -> str:
    """Генерация отчета по анализу диалогов"""
    if not messages:
        return "❌ Нет данных для анализа"

    total_messages = len(messages)
    unique_users = len(set(msg.get('user_id') for msg in messages if 'user_id' in msg))
    date_range = {
        'from': min(msg.get('timestamp', '') for msg in messages),
        'to': max(msg.get('timestamp', '') for msg in messages)
    }

    # Анализы
    state_analysis = analyze_state_transitions(messages)
    qualification_analysis = analyze_qualification_progress(messages)
    problems = find_problem_dialogs(messages)

    # Статистика по типам сообщений
    message_types = Counter(msg.get('message_type') for msg in messages)
    states_stats = Counter(msg.get('state') for msg in messages if 'state' in msg)

    report = f"""
📊 ОТЧЕТ АНАЛИЗА ДИАЛОГОВ
{'=' * 50}

📈 ОБЩАЯ СТАТИСТИКА:
• Всего сообщений: {total_messages}
• Уникальных пользователей: {unique_users}
• Период: {date_range['from'][:10]} - {date_range['to'][:10]}
• Сообщений на пользователя: {total_messages / unique_users:.1f}

📝 ТИПЫ СООБЩЕНИЙ:
"""
    for msg_type, count in message_types.most_common():
        report += f"• {msg_type}: {count}\n"

    report += f"\n🎯 СОСТОЯНИЯ ДИАЛОГОВ:\n"
    for state, count in states_stats.most_common():
        report += f"• {state}: {count}\n"

    report += f"\n🔄 ПЕРЕХОДЫ МЕЖДУ СОСТОЯНИЯМИ:\n"
    for transition, count in sorted(state_analysis['transitions'].items(),
                                   key=lambda x: x[1], reverse=True)[:10]:
        report += f"• {transition}: {count} раз\n"

    report += f"\n📊 КВАЛИФИКАЦИЯ КЛИЕНТОВ:\n"
    for qual, count in qualification_analysis['current_qualifications'].items():
        report += f"• {qual}: {count} пользователей\n"

    report += f"\nПрогрессия квалификации:\n"
    for progression, count in qualification_analysis['progression'].items():
        if count > 0:
            report += f"• {progression}: {count} переходов\n"

    if problems:
        report += f"\n🚨 ПРОБЛЕМНЫЕ ДИАЛОГИ ({len(problems)}):\n"
        for problem in problems[:5]:  # Показываем топ-5 проблем
            report += f"• Пользователь {problem['user_id']}: {problem['type']} "
            report += f"({problem.get('count', len(problem.get('details', [])))})\n"

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        report += f"\n💾 Отчет сохранен в: {output_file}\n"

    return report

def main():
    """Основная функция для запуска анализа"""
    import argparse

    parser = argparse.ArgumentParser(description="Анализ диалогов бота")
    parser.add_argument("--days", type=int, default=7,
                       help="Количество дней для анализа (по умолчанию: 7)")
    parser.add_argument("--user", type=str,
                       help="Анализ конкретного пользователя")
    parser.add_argument("--output", type=str,
                       help="Файл для сохранения отчета")
    parser.add_argument("--problems-only", action="store_true",
                       help="Показать только проблемные диалоги")

    args = parser.parse_args()

    print(f"📊 Загрузка логов за последние {args.days} дней...")
    messages = load_dialog_logs(args.days)

    if not messages:
        print("❌ Логи диалогов не найдены")
        return

    print(f"✅ Загружено {len(messages)} сообщений")

    if args.problems_only:
        problems = find_problem_dialogs(messages)
        if problems:
            print(f"\n🚨 Найдено {len(problems)} проблемных диалогов:\n")
            for problem in problems:
                print(f"👤 Пользователь: {problem['user_id']}")
                print(f"🔍 Проблема: {problem['type']}")
                print(f"⚠️ Серьезность: {problem['severity']}")
                if problem['type'] == 'multiple_greetings':
                    print(f"📊 Количество приветствий: {problem['count']}")
                print("---")
        else:
            print("✅ Проблемных диалогов не найдено")

    elif args.user:
        user_journey = analyze_user_journey(messages, args.user)
        if args.user in user_journey:
            print(f"\n👤 Диалог пользователя {args.user}:\n")
            for msg in user_journey[args.user]:
                msg_type = "👤" if msg['message_type'] == 'user' else "🤖"
                print(f"{msg_type} [{msg['state']}] {msg['timestamp'][:19]}")
                print(f"   {msg['text']}\n")
        else:
            print(f"❌ Пользователь {args.user} не найден")

    else:
        report = generate_report(messages, args.output)
        print(report)

if __name__ == "__main__":
    main()