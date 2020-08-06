import header
from random import shuffle

suit_list = ['♦', '♣', '♥', '♠']
value_list = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']
init_rank_list = [i for i in range(1, 53)]


# a single card
class Card():
    def __init__(self, rank, suit, value):
        self.__rank = rank
        self.__suit = suit
        self.__value = value

    def get_suit(self):
        return self.__suit

    def get_value(self):
        return self.__value

    def get_rank(self):
        return self.__rank

    def get_card(self):
        card = [self.__rank, self.__suit, self.__value]
        return card


def get_new_deck():
    deck = []
    rank = 1
    for value in value_list:
        for suit in suit_list:
            deck.append(Card(rank, suit, value))
            rank += 1
    return deck


def sort_by_init_rank(cards):
    return cards[0]


# a deck with 52 cards
class Deck():
    def __init__(self):
        self.__deck = get_new_deck()
        self.__cards_set = self.distribute()

    def shuffle(self):
        shuffle(self.__deck)

    def distribute(self, shuf=True):
        if shuf:
            self.shuffle()

        cards_set = [
            # the cards will be sorted by the rank:
            sorted(self.__deck[0:13], key=lambda c: c.get_rank()),
            sorted(self.__deck[13:26], key=lambda c: c.get_rank()),
            sorted(self.__deck[26:39], key=lambda c: c.get_rank()),
            sorted(self.__deck[39:52], key=lambda c: c.get_rank())
        ]
        return cards_set

    def get_deck(self):
        for c in self.__deck:
            card = c.get_card()
            print(card)

    def get_cards(self, player_no):
        return self.__cards_set[player_no]


def compare(list1, list2):
    pass

"""new_deck = Deck()
cards = new_deck.get_cards(0)
p = sorted(cards, key=lambda c: c.get_rank())

for p in cards:
    print(p.get_card())
"""

