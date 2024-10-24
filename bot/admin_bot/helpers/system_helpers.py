import psutil

def get_system_statistics():
    # ���������� ����������
    cpu_usage = psutil.cpu_percent(interval=1)

    # ���������� ����������� ������
    memory = psutil.virtual_memory()
    memory_usage = memory.percent

    # ���������� ��������� ������������
    disk = psutil.disk_usage('/')
    disk_usage = disk.percent

    # ���������� ����
    net_io = psutil.net_io_counters()
    sent_bytes = net_io.bytes_sent
    recv_bytes = net_io.bytes_recv

    # ��������� ����������
    return {
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage,
        'disk_usage': disk_usage,
        'sent_bytes': sent_bytes,
        'recv_bytes': recv_bytes
    }
