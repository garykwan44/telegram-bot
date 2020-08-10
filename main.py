import header
from game_engine import Game
from flask import Flask, request, Response
from threading import Thread
from time import sleep

# external
import functionality as funct
from functionality import write_json, parse_message, send_message

# token = '1343142606:AAG7_HsYBvPcT_UyGXQ2ytkaTCujBM4dumo'
app = Flask(__name__)
game_begin = False
new_game = None


@app.route('/', methods=['POST', 'GET'])
def index():
    global game_begin, new_game

    if request.method == 'POST':
        msg = request.get_json()
        type = list(msg.keys())

        write_json(msg, 'telegram_request.json')

        if 'message' in type and not game_begin:
            chat_id, symbol = parse_message(msg)
            user_id = msg['message']['from']['id']
            user_exists = funct.user_exists(user_id)

            print(symbol)

            if not symbol:
                # write_json(msg, 'telegram_request.json')
                pass

            elif symbol == 'signin':
                funct.add_account(msg)

            # Not Yet Finished
            elif symbol == 'start':
                if user_exists:
                    game_begin = funct.game_start(msg, True)  # Test mode is on.
                    print(game_begin)
                    if game_begin:

                        new_game = Game(-335838630)
                        new_game.begin()
                        t = Thread(target=new_game.in_game, args=())
                        t.start()
                    else:
                        send_message(chat_id, "Game ended.")



                else:
                    send_message(chat_id, "You haven't signed in!")

            elif symbol == 'term':
                if user_exists:
                    game_id = msg['message']['chat']['id']
                    funct.game_terminate(msg, game_id)
                else:
                    send_message(chat_id, "You haven't signed in!")

            elif symbol == 'join':
                if user_exists:
                    game_id = msg['message']['chat']['id']
                    funct.game_join(msg, game_id)
                else:
                    send_message(chat_id, "You haven't signed in!")

            else:
                funct.send_inline_keyboard(chat_id, 'hi', [[{'text': 'd', 'callback_data': 'ccc'}]])
                send_message(chat_id, 'Command not found.')




        # update = 'callback_query'
        elif 'callback_query' in type:
            # print(msg['callback_query']['id'])
            callback_data = msg['callback_query']['data']
            # print(callback_data)

            """Handler"""
            if callback_data == 'ccc':
                pass

            elif callback_data == 'ok':
                new_game.card_select_is_done(msg)

            elif callback_data == 'pass':
                new_game.pass_the_turn(msg)

            elif 1 <= int(callback_data) <= 52:
                new_game.card_select(callback_data, msg)


            funct.answer_callback_query(msg['callback_query']['id'])

        write_json(msg, 'telegram_request.json')
        return Response('ok', status=200)

    # localhost: 5000
    else:
        return '<h1>The bot is running...</h1>'


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
    # https://api.telegram.org/bot1343142606:AAG7_HsYBvPcT_UyGXQ2ytkaTCujBM4dumo/setWebhook?url=https://f2375c15c11f.ngrok.io
