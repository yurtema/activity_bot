import random

funcs = []
state = 'new_game'
comms = []


def message_handler(commands: list, strict=True):
    """
    Эаэ ну короче это типа декоратор, я сам уже не до конца помню как он работает.
    Если продекорированной функции дали в качестве text строку, в которой перый элемент есть в списке команд
    вернет результат выполнения этой продекорированной функции. Если нет, вернет нон.
    Если выключен стрикт, любое появление слова из списка команд в тексте стригерит обернутую функцию.
    """

    def _create_wrapper(f):
        def _wrapper(text, author_id):
            if strict:
                if text.split(' ')[0] in commands:
                    return f(text, author_id)
                return None
            else:
                if any([i in commands for i in text.split(' ')]):
                    return f(text, author_id)
                return None

        funcs.append(_wrapper)
        return _wrapper

    return _create_wrapper


@message_handler(commands=['/new_game'])
def new_game(text, author_id):
    """
    /new_game название_команды_1 название_команды_2...
    Наполняет scores командами после проверки на наличие аргументов
    """
    global scores, comms, state, last_command_pos

    author_id.find('')

    if len(text.split(' ')) < 3:
        return "Ну вы хотя бы вчетвером играйте (недостаточно команд)"

    # {код команды: очки, код команды: очки}
    scores = {}
    # [код команды, код команды]
    comms = []
    state = 'waiting_next'

    for com in text.split(' ')[1:]:
        comms.append(com)
        scores[com] = 0

    last_command_pos = 0

    return "Команды созданы, игра начата"


@message_handler(commands=['/next'])
def next_turn(text, author_id):
    global state, last_command_pos, comms, comm

    text.find(author_id)

    if state != 'waiting_next':
        return

    state = 'waiting_win1'

    comm = comms[last_command_pos % len(comms)]
    last_command_pos += 1

    return f'Команда {comm} \nСтраница {random.randint(1, 39)}, карточка {random.randint(1, 9)}, ' \
           f'{random.choice(["говорить", "показывать", "рисовать"])}\n' \
           f'Команда угадала за 60 секунд?'


@message_handler(commands=['да'])
def win1(text, author_id):
    # победила первая команда
    global state, scores, comm

    text.find(author_id)

    if state != 'waiting_win1':
        return

    scores[comm] += 2
    state = 'waiting_next'
    return f'Добавил два очка команде {comm}'


@message_handler(commands=['нет'])
def who_win2(text, author_id):
    # Спросить кто победил за вторую минуту
    global state, scores, comm

    text.find(author_id)

    if state != 'waiting_win1':
        return

    state = 'waiting_win2'
    return 'Кто угадал за вторую минуту?'


def win2(text, author_id):
    # Понять кто победил за вторую минуту
    global state, scores, comms
    author_id.find('')

    if state != 'waiting_win2':
        return

    if not (text in comms or text.lower() == 'никто'):
        return 'Я жду название команды либо слово никто'

    if text.lower() == 'никто':
        state = 'waiting_next'
        return 'Ну вы и лохи'

    state = 'waiting_next'
    scores[text] += 1
    return f'Добавил очко команде {text}'


funcs.append(win2)


@message_handler(commands=['/scores'])
def send_scores(text, author_id):
    global scores
    text.find(author_id)

    try:
        out = ''.join([f'{com}: {scores[com]}\n' for com in scores])
    except NameError:
        return 'Вы и игру еще не начали, дурни'

    return out


def responde(text, author_id):
    """Функция, вызываемая снаружи. Прогоняет текст по всем функциям-хэндлерам, возвращает результат"""

    out = [res for i in funcs if (res := i(text, author_id))]

    if out:
        return out[0]
    else:
        return 'Нихера не понятно (команда не распознана)'
