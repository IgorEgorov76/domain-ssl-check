import requests
from datetime import datetime, timezone
import sys
import os

# Функция для получения данных о домене
def get_domain_info(domain, api_key):
    url = f'https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey={api_key}&domainName={domain}&outputFormat=JSON'
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error retrieving data for domain {domain}: {response.status_code} - {response.text}")
        return None

# Функция для вычисления оставшихся дней до окончания домена
def days_until_expiration(expiration_date):
    expiration_date = expiration_date.split('T')[0]  # Берем только дату
    expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
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

    api_key = 'your_key'

    successful_domains = []
    failed_domains = []

    # Обработка доменов
    for domain in domains:
        domain_info = get_domain_info(domain, api_key)
        if domain_info:
            if 'WhoisRecord' in domain_info and 'registryData' in domain_info['WhoisRecord']:
                expires_date = domain_info['WhoisRecord']['registryData'].get('expiresDate')
                if expires_date:
                    remaining_days = days_until_expiration(expires_date)
                    formatted_date = datetime.strptime(expires_date.split('T')[0], '%Y-%m-%d').strftime('%d %B %Y')
                    successful_domains.append(f"{domain} - {formatted_date} ({remaining_days} days remaining)")
                else:
                    failed_domains.append(f"{domain} - No expiration date found.")
            else:
                failed_domains.append(f"{domain} - No Whois record found.")
        else:
            failed_domains.append(f"{domain} - Failed to retrieve information.")

    write_results(f'{results_dir}/domain_expiration_dates.txt', successful_domains, failed_domains)  # Путь к выходному файлу