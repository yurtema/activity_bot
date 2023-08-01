import random

import requests
import json

funcs = []
state = 'new_game'


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
    global scores, coms, state, last_command_pos

    author_id.find('')

    if len(text.split(' ')) < 3:
        return "Ну вы хотя бы вчетвером играйте (недостаточно команд)"

    # {код команды: очки, код команды: очки}
    scores = {}
    # [код команды, код команды]
    coms = []
    state = 'waiting_next'

    for com in text.split(' ')[1:]:
        coms.append(com)
        scores[com] = 0

    last_command_pos = 0

    return "Команды созданы, игра начата"


@message_handler(commands=['/next'])
def next_turn(text, author_id):
    global state, last_command_pos, coms

    text.find(author_id)

    if state != 'waiting_next':
        return 'Сейчас не время использовать эту команду епта'

    state = 'waiting_next'

    com = coms[last_command_pos % len(coms)]
    last_command_pos += 1

    return f'Команда {com} \nСтраница {random.randint(1, 39)}, карточка {random.randint(1, 9)}, ' \
           f'{random.choice(["говорить", "показывать", "рисовать"])}\n'


def responde(text, author_id):
    """Функция, вызываемая снаружи. Прогоняет текст по всем функциям-хэндлерам, возвращает результат"""

    out = [res for i in funcs if (res := i(text, author_id))]

    if out:
        return out[0]
    else:
        return 'Нихера не понятно (команда не распознана)'
