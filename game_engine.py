import header
import firestore
import time
import card
import threading
from card import Card, Deck
from random import shuffle
from functionality import send_inline_keyboard, edit_inline_keyboard, send_message, delete_message
from copy import deepcopy

colltn = firestore.colltn_list()  # 'User', 'Game'


class Player():
    def __init__(self, player_id, cards):
        self.__player_id = player_id  # Type: int
        self.__cards = cards  # Type: list(card). initially 13 Card objects in a list
        self.__round_cards = []  # Type: list(card). the player's choices in his/her round
        self.__round_cards_button = self.display_cards_button()
        self.__win = False
        self.__winner_rank = 0

    # When a game starts, if the player initially has '♦3', then he/she will be the first player of the sequence:
    def first_start(self):
        # the first_card is the smallest card:
        first_card = self.__cards[0]
        if first_card.get_rank() == 1:
            return True
        else:
            return False

    def get_player_id(self):
        return self.__player_id

    def get_cards(self):
        return self.__cards

    def add_round_cards(self, card):
        self.__round_cards.append(card)

    def get_round_cards(self):
        return self.__round_cards

    # Clear all the round_cards:
    def clear_round_cards(self):
        self.__round_cards.clear()

    # Remove the specified card in the round_cards:
    def remove_round_cards(self, card):
        self.__round_cards.remove(card)

    # Remove the used cards:
    def remove_used_cards(self, cards):
        for c in cards:
            self.__cards.remove(c)

    # Return str
    def display_round_cards(self):
        text = ''
        for c in self.__round_cards:
            text += (c.get_suit() + c.get_value() + ' ')
        return text

    # Return str
    def display_cards(self):
        text = ''
        for c in self.__cards:
            text += (c.get_suit() + c.get_value() + ' ')
        return text

    # Return an array of an array
    def display_cards_button(self):
        if len(self.__cards) == 0:
            return None

        col = 4
        row = len(self.__cards) // col
        index = 0
        display = []

        for i in range(row):
            temp = []
            for j in range(col):
                pattern = self.__cards[index].get_suit() + self.__cards[index].get_value()
                temp.append({'text': pattern, 'callback_data': self.__cards[index].get_rank()})
                index += 1
            display.append(temp)

        if len(self.__cards) % col:
            temp = []
            for i in self.__cards[index:]:
                pattern = i.get_suit() + i.get_value()
                temp.append({'text': pattern, 'callback_data': i.get_rank()})
            display.append(temp)

        display.append([{'text': 'pass', 'callback_data': 'pass'}, {'text': 'ok', 'callback_data': 'ok'}])

        self.__round_cards_button = display
        return self.__round_cards_button

    def card_selected_button(self, rank):
        k = deepcopy(self.__round_cards_button)

        for row in k:
            for col in row:
                if col['callback_data'] == rank:
                    col['text'] = col['text'] + u'\u2611\uFE0F'
                    break
        self.__round_cards_button = k

        return self.__round_cards_button

    def card_deselected_button(self, rank):
        k = deepcopy(self.__round_cards_button)

        for row in k:
            for col in row:
                if col['callback_data'] == rank:
                    col['text'] = col['text'].replace(u'\u2611\uFE0F', '')
                    break
        self.__round_cards_button = k

        return self.__round_cards_button

    def is_win(self):
        return self.__win

    def set_win(self):
        self.__win = True

    def get_winner_rank(self):
        return self.__winner_rank

    def set_winner_rank(self, winner_rank):
        self.__winner_rank = winner_rank

class Game():
    def __init__(self, game_id):
        self.__game_id = game_id  # Type: int
        self.__init_deck = Deck()  # Type: Deck obj. The deck with 52 cards.
        self.__used_cards = []  # Type: list(Card). The cards that are used.
        self.__round = 1
        self.__players = self.add_players()  # 4 players in the game.
        self.__sequence = self.set_sequence()
        self.__current_cards = []  # Type: list(Card). The cards on the table.
        self.__current_cards_owner = self.__sequence[0]  # Who gives out the current cards
        self.__current_round_player = self.__sequence[0]  # Type: Player obj. The player of the current round.
        self.__next_turn = True  # If a player tapped 'ok' or 'pass' -> True
        self.__game_end = False
        self.__winner_rank = 1

    def add_players(self):
        game = firestore.get_record(colltn[1], str(self.__game_id))
        players = [
            Player(game['player']['player01'], self.__init_deck.get_cards(0)),
            Player(game['player']['player02'], self.__init_deck.get_cards(1)),
            Player(game['player']['player03'], self.__init_deck.get_cards(2)),
            Player(game['player']['player04'], self.__init_deck.get_cards(3))
        ]
        return players

    # get an individual player from the list. player_id: int
    def get_player(self, player_id):
        for player in self.__players:
            pid = player.get_player_id()
            if pid == player_id:
                return player
        return None

    def get_current_round_player(self):
        return self.__current_round_player

    # Return str
    def display_current_cards(self):
        text = ''
        for c in self.__current_cards:
            text += (c.get_suit() + c.get_value() + ' ')
        return text

    def set_current_cards(self, cards):
        self.__current_cards = deepcopy(cards)

    def set_sequence(self):
        queue = self.__players.copy()
        shuffle(queue)

        for player in queue:
            if player.first_start():
                queue.remove(player)
                queue.insert(0, player)
                break
        return queue

    def timer(self, target_time):
        start_time = time.time()
        while True:
            if self.__next_turn:
                break

            current_time = time.time()
            diff = current_time - start_time
            print(diff)

            if diff >= target_time:
                print('Time up!')
                self.__next_turn = True
                break
            time.sleep(1)

    def begin(self):
        firestore.update_record(colltn[1], str(self.__game_id), {'start': True})

        # show the starting cards to the players:
        for player in self.__players:
            k = player.display_cards()
            send_message(player.get_player_id(), 'Starting Cards:\n' + k)
            # send_inline_keyboard(player.get_player_id(), 'Starting cards:', k)
            # print(k)

    # If a card is selected by a player in his/her round, or used by a player, that card is said to be 'used'.
    # card_rank: str
    def card_select(self, card_rank, message):
        current_round_player = self.__current_round_player
        card = self.__init_deck.get_card(int(card_rank))

        chat_id = current_round_player.get_player_id()
        message_id = message['callback_query']['message']['message_id']
        text = 'The cards on the desk: ' + self.display_current_cards()

        if card not in self.__used_cards:
            current_round_player.add_round_cards(card)
            self.__used_cards.append(card)
            print(current_round_player.get_round_cards())

            k = current_round_player.card_selected_button(int(card_rank))
            print(k)
            edit_inline_keyboard(chat_id, message_id, text, k)

        else:
            current_round_player.remove_round_cards(card)
            self.__used_cards.remove(card)
            print(current_round_player.get_round_cards())

            k = current_round_player.card_deselected_button(int(card_rank))
            print(k)
            edit_inline_keyboard(chat_id, message_id, text, k)

    # If the player taps the 'ok' button:
    def card_select_is_done(self, message):
        current_round_player = self.__current_round_player
        valid, greater = card.compare(self.__current_cards, current_round_player.get_round_cards())

        print(valid, greater)
        if valid and greater:
            cards = current_round_player.get_round_cards()
            self.set_current_cards(cards)
            current_round_player.remove_used_cards(cards)
            current_round_player.clear_round_cards()

            # show_text = current_round_player.display_round_cards()
            # send_message(current_round_player.get_player_id(), show_text)
            message_id = message['callback_query']['message']['message_id']
            delete_message(current_round_player.get_player_id(), message_id)

            if not current_round_player.get_cards():
                current_round_player.set_win()
                current_round_player.set_winner_rank(self.__winner_rank)

                text = 'Congrats! Your rank: ' + str(self.__winner_rank)
                send_message(current_round_player.get_player_id(), text)
                self.__winner_rank += 1
                # next player:
                self.__current_cards_owner = self.__sequence[0]

            else:
                self.__current_cards_owner = current_round_player

            self.__next_turn = True

        else:
            send_message(current_round_player.get_player_id(), 'Invalid cards.')

    def pass_the_turn(self, message):
        current_round_player = self.__current_round_player

        if self.__current_cards_owner == current_round_player:
            send_message(current_round_player.get_player_id(), 'You cannot pass.')
        else:
            current_round_player.clear_round_cards()
            message_id = message['callback_query']['message']['message_id']
            delete_message(current_round_player.get_player_id(), message_id)
            self.__next_turn = True

    def in_game(self):
        while True:
            current_round_player = self.__sequence.pop(0)

            if not self.__sequence:
                self.__next_turn = False
                current_round_player.set_win()
                current_round_player.set_winner_rank(self.__winner_rank)
                break

            if self.__next_turn:
                self.__next_turn = False

                if current_round_player == self.__current_cards_owner:
                    self.__current_cards.clear()

                if not self.__current_cards:
                    text = 'Nothing is on the desk!'
                else:
                    text = 'The cards on the desk: ' + self.display_current_cards()

                self.__current_round_player = current_round_player
                k = current_round_player.display_cards_button()
                send_inline_keyboard(current_round_player.get_player_id(), "It's your turn!\n" + text, k)
                print(k)

                # timer = threading.Thread(target=self.timer, args=(15,))
                # timer.start()
                # timer.join()
                
                if not current_round_player.is_win():
                    self.__sequence.append(current_round_player)

            time.sleep(1)
        print('game_end')

"""
        while not self.__game_end:
            player_this_turn = self.__sequence.pop(0)
            # print(player_this_turn)

            thread1 = threading.Thread(target=self.check_next_turn, args=())
            thread2 = threading.Thread(target=self.timer, args=(10,))

            thread1.start()
            thread2.start()
            thread2.join()
            print('turn end.')

            time.sleep(2)
            self.__next_turn = False
            firestore.update_record(colltn[1], str(self.__game_id), {'next_turn': False})

            # if the player wins, pop it. Otherwise:
            self.__sequence.append(player_this_turn)
            self.__round += 1
"""

"""Not Yet Finished"""

# new_Game = Game(855480841)
# new_Game.game_begin()

"""new_deck = Deck(False)
gary = Player('556', new_deck.get_cards(0))
k = gary.display_cards_button()

k = gary.card_selected_button('3')

import json
with open('display_cards.json', 'w') as f:
    json.dump(k, f, indent=4, ensure_ascii=True)
print(k)

# send_inline_keyboard(855480841, 'hi', k)"""


