# calculations.py

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
