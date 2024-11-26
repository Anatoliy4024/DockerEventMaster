# Метод для расчета длительности
from datetime import datetime

def get_duration(start_time, end_time):
    if start_time and end_time:
        start_time = datetime.strptime(start_time, '%H:%M')
        end_time = datetime.strptime(end_time, '%H:%M')
        duration_minutes = (end_time - start_time).seconds // 60
        duration_hours = (duration_minutes // 60) + (1 if duration_minutes % 60 != 0 else 0)
        return duration_hours
    return 0

# calculations

def calculate_total_cost(duration, people_count):
    # Базовая стоимость
    base_cost = 160

    # Дополнительные часы
    additional_hours = max(0, duration - 2) * 30

    # Дополнительные персоны
    additional_persons = max(0, people_count - 2) * 20

    # Итоговая стоимость
    total_cost = base_cost + additional_hours + additional_persons

    return total_cost
