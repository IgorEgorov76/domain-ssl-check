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

    print(f"Data successfully written to {file_path}")

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
            remaining_days = days_until_expiration(expiration_date)
            formatted_date = datetime.strptime(expiration_date.replace(" GMT", ""), '%b %d %H:%M:%S %Y').strftime('%d %B %Y')
            successful_ssl_domains.append(f"{domain} - {formatted_date} ({remaining_days} days remaining)")
        else:
            failed_ssl_domains.append(f"{domain} - Failed to retrieve certificate information.")

    write_results(f'{results_dir}/ssl_expiration_dates.txt', successful_ssl_domains, failed_ssl_domains)  # Путь к выходному файлу