import header
import firestore
import time
import threading
from random import shuffle
from functionality import send_inline_keyboard
from card import Card, Deck

colltn = firestore.colltn_list()  # 'User', 'Game'


class Player():
    def __init__(self, player_id, cards):
        self.__player_id = player_id
        self.__cards = cards  # initially 13 Card objects in a list
        self.__round_cards = []  # the player's choices in his/her round

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

    def add_round_cards(self, card):
        self.__round_cards.append(card)

    # Clear the round_cards:
    def clear_round_cards(self):
        self.__round_cards.clear()

    # Remove the specified card in the round_cards:
    def remove_round_cards(self, card):
        self.__round_cards.remove(card)

    # Return an array of an array
    def display_cards(self):
        if len(self.__cards) == 0:
            return None

        col = 5
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
        return display


class Game():
    def __init__(self, game_id):
        self.__game_id = game_id
        self.__init_deck = Deck()               # The deck with 52 cards.
        self.__current_cards = []               # The cards on the table.
        self.__round = 1
        self.__players = self.add_players()     # 4 players in the game.
        self.__sequence = self.set_sequence()
        self.__next_turn = False                # If a player tapped 'ok' or 'pass' -> True
        self.__game_end = False

    def add_players(self):
        game = firestore.get_record(colltn[1], str(self.__game_id))
        players = [
            Player(game['player']['player01'], self.__init_deck.get_cards(0)),
            Player(game['player']['player02'], self.__init_deck.get_cards(1)),
            Player(game['player']['player03'], self.__init_deck.get_cards(2)),
            Player(game['player']['player04'], self.__init_deck.get_cards(3))
        ]
        return players

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
                break
            time.sleep(1)

    # Check if the player of the current turn has tapped the 'ok':
    def check_next_turn(self):
        while not self.__next_turn:
            next_turn = firestore.get_record(colltn[1], str(self.__game_id))['next_turn']
            if next_turn:
                self.__next_turn = True
            else:
                self.__next_turn = False
        time.sleep(1)

    def game_begin(self):
        firestore.update_record(colltn[1], str(self.__game_id), {'start': True})

        # show the starting cards to the players:
        for player in self.__players:
            k = player.display_cards()
            send_inline_keyboard(player.get_player_id(), 'Starting cards:', k)
            print(k)


    def new_turn(self, player):
        if not self.__sequence:
            pass


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

"""new_deck = Deck()
gary = Player('556', new_deck.get_cards(0))
k = gary.display_cards()
print(k)

send_inline_keyboard(855480841, 'hi', k)
"""
