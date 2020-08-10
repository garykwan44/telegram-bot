import header
import json
import requests
import re
import firestore
import time
# import game_engine
from timer import timer

token = '1343142606:AAG7_HsYBvPcT_UyGXQ2ytkaTCujBM4dumo'
colltn = firestore.colltn_list()  # 'User', 'Game'


def write_json(data, filename='response.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=True)


def parse_message(message):
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']

    pattern = r'/[a-zA-Z]{2,}'
    ticker = re.findall(pattern, txt)

    if ticker:  # if not empty
        symbol = ticker[0][1:]
    else:
        symbol = ''

    return chat_id, symbol


def send_message(chat_id, text='sth'):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}

    r = requests.post(url, json=payload)
    return r


def delete_message(chat_id, message_id):
    url = f'https://api.telegram.org/bot{token}/deleteMessage'
    payload = {
        'chat_id': chat_id,
        'message_id': message_id
    }
    r = requests.post(url, json=payload)
    return r


def answer_callback_query(callback_id, text='Command confirmed.'):
    url = f'https://api.telegram.org/bot{token}/answerCallbackQuery'
    payload = {
        'callback_query_id': callback_id,
        'text': text
    }
    r = requests.post(url, json=payload)
    return r


# Not Yet Finished
# inline_k is a list of dicts
def send_inline_keyboard(chat_id, text, inline_k):
    payload = {
        'chat_id': chat_id,
        'text': text,
        'reply_markup': {
            'inline_keyboard': inline_k,
        }
    }
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    r = requests.post(url, json=payload)
    return r


def edit_inline_keyboard(chat_id, message_id, text, inline_k):
    payload = {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': text,
        'reply_markup': {
            'inline_keyboard': inline_k
        }
    }
    url = f'https://api.telegram.org/bot{token}/editMessageText'
    r = requests.post(url, json=payload)
    return r



def add_account(message):
    is_bot = message['message']['from']['is_bot']

    if not is_bot:
        user_id = message['message']['from']['id']
        record = firestore.get_record(colltn[0], str(user_id))

        if record is None:
            user_name = message['message']['from']['username']
            user_first_name = message['message']['from']['first_name']

            info = {
                'username': user_name,
                'first_name': user_first_name,
                'asset': 100
            }
            firestore.add_record(colltn[0], str(user_id), info)
            send_message(message['message']['chat']['id'], 'Success.')

        else:
            send_message(message['message']['chat']['id'], 'This user has already existed.')

    # not be added if it is a bot:
    else:
        send_message(message['message']['chat']['id'], 'Error.')


def user_exists(user_id):
    user = firestore.get_record(colltn[0], str(user_id))
    if user is not None:
        return True
    else:
        return False


"""Game Settings"""


def game_exists(game_id):
    game = firestore.get_record(colltn[1], str(game_id))
    if game is not None:
        return True
    else:
        return False

def game_is_running(game_id):
    start = firestore.get_record(colltn[1], str(game_id))['start']
    if start:
        return True
    else:
        return False


# Not yet finished: game engine
def game_start(message, test_mode=False):
    if test_mode:
        return True

    game_id = message['message']['chat']['id']  # use the chat_id (in group) as the game_id

    # check if the game has been called:
    game_called = game_exists(game_id)
    if not game_called:
        owner_id = message['message']['from']['id']  # the user who starts the game

        player = {
            'player01': owner_id
        }

        info = {
            'owner': owner_id,
            'start': False,
            'next_turn': False,  # if a player selected the cards and tapped 'ok', then 'next_turn' -> 'True'
            'no_of_player': 1,
            'player': player
        }
        firestore.add_record(colltn[1], str(game_id), info)

        owner = firestore.get_record(colltn[0], str(owner_id))['first_name']
        msg = owner + ' is calling the game!\nGame id: ' + str(game_id)
        send_message(message['message']['chat']['id'], msg)

        # wait until the Firestore: start->True

        # declaration of the start of the game
        return True

    else:
        msg = 'The game (Game id: ' + str(game_id) + ') has already been called!'
        send_message(message['message']['chat']['id'], msg)


def game_terminate(message, game_id):
    game = firestore.get_record(colltn[1], str(game_id))

    # if the game exists:
    if game is not None:
        start = game['start']

        # if the start has already been started, then no one can terminate the game.
        if not start:
            owner_id = game['owner']
            initiator_id = message['message']['from']['id']  # the user who wishes to terminate the existing game

            # if the initiator is the owner of the game:
            if initiator_id == owner_id:
                firestore.delete_doc(colltn[1], str(game_id))
                send_message(message['message']['chat']['id'], 'The game has been terminated.')

            else:
                send_message(message['message']['chat']['id'], "You don't have authorization.")
        else:
            send_message(message['message']['chat']['id'], "You can't terminate the game that has been started.")
    else:
        send_message(message['message']['chat']['id'], "No games is running.")


# Not yet finished: duplicated players
def game_join(message, game_id):
    game = firestore.get_record(colltn[1], str(game_id))

    # if the game exists:
    if game is not None:
        user_id = message['message']['from']['id']
        first_name = message['message']['from']['first_name']
        no_of_player = game['no_of_player'] + 1

        new_player = 'player0' + str(no_of_player)

        firestore.update_record(colltn[1], str(game_id), {'no_of_player': no_of_player})
        firestore.update_record(colltn[1], str(game_id), {'player': {new_player: user_id}})

        msg = 'Player ' + first_name + ' has joined the game!'
        send_message(message['message']['chat']['id'], msg)

    else:
        send_message(message['message']['chat']['id'], "No games is running.")


from telegram import message, Bot
bot = Bot('1343142606:AAG7_HsYBvPcT_UyGXQ2ytkaTCujBM4dumo')

def send():
    p = bot.sendMessage(855480841, 'hi')
    print(p)










# Not yet finished: flee the game
def say():
    while True:
        print('hi')
        time.sleep(1)

# send_message(855480841, u'\u2665\ufe0f')