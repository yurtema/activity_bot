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


@message_handler(commands=['/newgame'])
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
        comms.append(com.lower())
        scores[com.lower()] = 0

    last_command_pos = 0

    return 'Команды созданы, игра начата&' \
           'reply_markup={"is_persistent": true, "resize_keyboard": true,' \
           f'"keyboard":[["/next"]]' \
           '}'.replace("'", '"')


@message_handler(commands=['/next'])
def next_turn(text, author_id):
    global state, last_command_pos, comm

    text.find(author_id)

    if state != 'waiting_next':
        return

    state = 'waiting_win1'

    comm = comms[last_command_pos % len(comms)]
    last_command_pos += 1

    keys = ['да', 'нет']

    return f'Команда {comm} \nСтраница {random.randint(1, 39)}, карточка {random.randint(1, 9)}, ' \
           f'{random.choice(["говорить", "показывать", "рисовать"])}\n' \
           f'Команда угадала за 60 секунд?&' \
           'reply_markup={"is_persistent": true, "resize_keyboard": true,' \
           f'"keyboard":[{keys}]' \
           '}'.replace("'", '"')


@message_handler(commands=['да'])
def win1(text, author_id):
    # победила первая команда
    global state, scores

    text.find(author_id)

    if state != 'waiting_win1':
        return

    scores[comm] += 2
    state = 'waiting_next'
    return f'Добавил два очка команде {comm}&' \
           'reply_markup={"is_persistent": true, "resize_keyboard": true,' \
           f'"keyboard":[["/next"]]' \
           '}'.replace("'", '"')


@message_handler(commands=['нет'])
def who_win2(text, author_id):
    # Спросить кто победил за вторую минуту
    global state

    text.find(author_id)

    if state != 'waiting_win1':
        return
    state = 'waiting_win2'
    return 'Кто угадал за вторую минуту?&' \
           'reply_markup={"is_persistent": true, "resize_keyboard": true,' \
           f'"keyboard":[{comms + ["никто"]}]' \
           '}'.replace("'", '"')


def win2(text_, author_id):
    # Понять кто победил за вторую минуту
    global state, scores
    author_id.find('')
    text = text_.lower()
    if state != 'waiting_win2':
        return

    if not (text in comms or text == 'никто'):
        return 'Я жду название команды либо слово никто'

    if text == 'никто':
        state = 'waiting_next'
        return 'Ну вы и лохи&' \
               'reply_markup={"is_persistent": true, "resize_keyboard": true,' \
               f'"keyboard":[["/next"]]' \
               '}'.replace("'", '"')

    state = 'waiting_next'
    scores[text] += 1
    return f'Добавил очко команде {text}&' \
           'reply_markup={"is_persistent": true, "resize_keyboard": true,' \
           f'"keyboard":[["/next"]]' \
           '}'.replace("'", '"')


funcs.append(win2)


@message_handler(commands=['/scores'])
def send_scores(text, author_id):
    text.find(author_id)

    try:
        out = ''.join([f'{com}: {scores[com]}\n' for com in scores])
    except NameError:
        return 'Вы и игру еще не начали, дурни'

    return out


@message_handler(commands=['/set'])
def set_score(text, author_id):
    global scores

    text.find(author_id)
    args = text.split(' ')[1:]

    if len(args) != 2:
        return 'Мне нужно два аргумента: название команды и сколько очков им установить'
    if args[0] not in comms:
        return 'Я не знаю такой команды'
    try:
        args[1] = int(args[1])
    except ValueError:
        return 'Второй аргумент должен быть числом'

    scores[args[0]] = args[1]
    return f'Успешно установил счет команды {args[0]} на {args[1]}'


@message_handler(commands=['/help', '/start'])
def send_help(text, author_id):
    text.find(author_id)

    return '/newgame <название 1 команды> <название 2 команды> ... Начинает новую игру, СТИРАЕТ СТАРУЮ \n' \
           '/next ролит следующий ход \n' \
           '/set <название команды> <сколько очков установить> Устанавливает команде заданное количество очков'


def responde(text, author_id):
    """Функция, вызываемая снаружи. Прогоняет текст по всем функциям-хэндлерам, возвращает результат"""

    out = [res for i in funcs if (res := i(text, author_id))]

    if out:
        return out[0]
    else:
        return 'Нихера не понятно (команда не распознана)'
