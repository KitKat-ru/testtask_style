import datetime
import requests
from bs4 import BeautifulSoup
import signal
import traceback
# from utils.logging_parser import logging
import logging

# словарь для хранения ссылок и их проверки
visited = {}
# сдоварь статистики
stats = {
    'all': 0
}
# кортеж со списком игнорируемых расширений при парсинге
ignore_list = ('.css', '.js', '.jpg', '.png', '.gif', 'ftp', 'linkedin', '127.0.0.1')
# кортеж со списком начальных ссылок для парсинга
my_list_links = ("https://www.djangoproject.com/", 'https://novi.kupujemprodajem.com/')


def signal_handler(signal, frame):
    """Выводит статистику по количеству охваченных ссылок."""
    logging.info("\nKeyboardInterrupt detected. Data:")
    logging.info(30 * '-')
    logging.info('Статистика по пройденым ссылкам')
    logging.info(stats)
    logging.info(30 * '-')
    logging.info('Словарь обойденных URL')
    logging.info(visited)
    exit(0)


signal.signal(signal.SIGINT, signal_handler)


def process_links(links):
    """Рекурсивная функция для перехода по ссылкам."""
    for link in links:
        # если ссылка уже обрабатывалась, пропускаем ее
        if link in visited:
            continue

        # обрабатываем ссылку
        logging.info(f"Processing {link}...")
        response = requests.get(link, timeout=2)
        status_code = response.status_code
        visited[link] = status_code

        stats['all'] += 1
        if status_code in stats:
            stats[status_code] += 1
        else:
            stats[status_code] = 1

        # если обработка прошла успешно, ищем ссылки на странице и обрабатываем их
        if status_code == 200:
            try:
                logging.info(f"Successfully processed {link}.")
                new_links = extract_links(response.content)
                current_depth = len(traceback.extract_stack()) - 1
                logging.info(f'Глубина рекурсии - {current_depth}')
                # Ограничиваем рекурсию
                if current_depth > 4:
                    break
                else:
                    process_links(new_links)
            except Exception as e:
                logging.error(f"exceptions {e}.")
                continue
        elif status_code == 999:
            logging.error(f"выходим из ветвления = {status_code} - {link}.")
            # process_links(new_links)
            break
        else:
            logging.error(f"status_code = {status_code} - {link}.")
            continue


def extract_links(content):
    soup = BeautifulSoup(content, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.startswith(('http', 'https')) and not any(ext in href for ext in ignore_list):
            links.append(href)
    return set(links)


if __name__ == '__main__':
    now = datetime.datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    logging.basicConfig(
        level=logging.INFO,
        filename=f'./logs/{formatted_date}_parser_links.log',
        encoding='utf-8',
        format='%(asctime)s, %(levelname)s, %(funcName)s, %(message)s'
    )

    process_links(my_list_links)
