import ssl
import socket
from datetime import datetime, timezone
import sys
import os

# Функция для получения даты истечения SSL сертификата
def get_ssl_certificate_expiration_date(domain_name):
    try:
        # Создаем SSL контекст
        context = ssl.create_default_context()

        # Устанавливаем соединение с сервером
        with socket.create_connection((domain_name, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=domain_name) as ssock:
                # Получаем сертификат
                cert = ssock.getpeercert()
                return cert['notAfter']
    except Exception as e:
        print(f"Error retrieving certificate for {domain_name}: {e}")
        return None

# Функция для вычисления оставшихся дней до окончания
def days_until_expiration(expiration_date):
    # Удаляем "GMT" и разбираем дату
    expiration_date = expiration_date.replace(" GMT", "")
    expiration_date = datetime.strptime(expiration_date, '%b %d %H:%M:%S %Y').replace(tzinfo=timezone.utc)
    remaining_days = (expiration_date - datetime.now(timezone.utc)).days
    return remaining_days

# Функция для чтения доменов из файла
def read_domains(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"Error: {file_path} file not found.")
        sys.exit(1)

# Функция для записи результатов в файл
def write_results(file_path, successful_domains, failed_domains):
    with open(file_path, 'w', encoding='utf-8') as output_file:
        output_file.write("Successfully Processed Domains:\n")
        for index, entry in enumerate(successful_domains, start=1):
            output_file.write(f"{index}. {entry}\n")

        output_file.write("\nFailed to Process Domains:\n")
        for index, entry in enumerate(failed_domains, start=1):
            output_file.write(f"{index}. {entry}\n")

    print(f"Data successfully written tdomain in domainso {file_path}")

# Основной код
if __name__ == "__main__":
    # Проверка и создание папки results
    results_dir = '../results'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    domains = read_domains('../domains.txt')  # Путь к файлу с доменами

    if not domains:
        print("The domains.txt file is empty. Please add some domains.")
        sys.exit(1)

    successful_ssl_domains = []
    failed_ssl_domains = []

    # Обработка доменов
    for domain in domains:
        expiration_date = get_ssl_certificate_expiration_date(domain)
        if expiration_date:
            # Преобразуем дату в объект datetime
            expiration_datetime = datetime.strptime(expiration_date.replace(" GMT", ""), '%b %d %H:%M:%S %Y').replace(tzinfo=timezone.utc)
            formatted_date = expiration_datetime.strftime('%d.%m.%y')
            successful_ssl_domains.append((domain, expiration_datetime, formatted_date))
        else:
            failed_ssl_domains.append(f"{domain} - Failed to retrieve certificate information.")

    # Сортируем успешные домены по дате истечения
    successful_ssl_domains.sort(key=lambda x: x[1])  # Сортируем по оригинальной дате

    # Форматируем вывод для записи в файл
    formatted_successful_ssl_domains = [f"{domain} - {formatted_date}" for domain, _, formatted_date in successful_ssl_domains]

    write_results(f'{results_dir}/ssl_expiration_dates.txt', formatted_successful_ssl_domains, failed_ssl_domains)  # Путь к выходному файлу