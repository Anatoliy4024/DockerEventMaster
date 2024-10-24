import psutil

def get_system_statistics():
    # Статистика процессора
    cpu_usage = psutil.cpu_percent(interval=1)

    # Статистика оперативной памяти
    memory = psutil.virtual_memory()
    memory_usage = memory.percent

    # Статистика дискового пространства
    disk = psutil.disk_usage('/')
    disk_usage = disk.percent

    # Статистика сети
    net_io = psutil.net_io_counters()
    sent_bytes = net_io.bytes_sent
    recv_bytes = net_io.bytes_recv

    # Формируем результаты
    return {
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage,
        'disk_usage': disk_usage,
        'sent_bytes': sent_bytes,
        'recv_bytes': recv_bytes
    }
