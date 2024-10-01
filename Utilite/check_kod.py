import os
import chardet

# Указать директорию проекта в которой надо проверить кодировку
directory = r'C:\Users\USER\PycharmProjects\Docker_Event_Master\bot\picnic_bot'

# Функция для проверки кодировки всех файлов
for root, dirs, files in os.walk(directory):
    for file in files:
        file_path = os.path.join(root, file)
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            print(f'File: {file_path}, Encoding: {encoding}')
