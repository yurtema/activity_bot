import request
import time
import private
from updates_manager import responde

# Получить изначальный offset
r = requests.get(f'https://api.telegram.org/bot{private.token}/getUpdates').json()['result']
if r:
    offset = r[-1]['update_id'] + 1
else:
    offset = 0

print(f'[{time.asctime()}] Bot started')


def handle_updates():
    """
    Функция запрашивает новые сообщения с апи тг с помощью offset, прогоняет по условиям для генерации ответа.
    Ничего не возвращает, в конце сама отсылает нужные сообщения.
    Работает с одним апдейтом за раз.
    """

    global offset

    # Попробовать тыкнуть апи телеги, чтобы получить новые сообщения.
    # Если чето пойдет не так, подождать минуту и тыкнуть снова.
    try:
        update = requests.get(f'https://api.telegram.org/bot{private.token}/'
                              f'getUpdates?offset={offset}').json()['result']
    except requests.exceptions.ConnectionError:
        time.sleep(60)
        return

    # Если никаких новых сообщений нет, ничего не делать (нет, что вы, какая излишняя документация?)
    if not update:
        return

    update = update[0]
    offset = update['update_id'] + 1
    text = update['message']['text']
    author_id = str(update['message']['chat']['id'])

    print(f'[{time.asctime()}] {author_id}: {text}')

    # Прокатить команду по responde для получения строчки с ответом и отправить запрос на апи для публикации сообщения.
    requests.post(f'https://api.telegram.org/bot{private.token}/sendMessage?chat_id={author_id}&'
                  f'text={responde(text, author_id)}')


while True:
    handle_updates()
