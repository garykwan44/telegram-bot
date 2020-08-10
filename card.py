import header
import copy
from random import shuffle

uni_suit_list = [u'\u2666\uFE0F', u'\u2663\uFE0F', u'\u2665\uFE0F', u'\u2660\uFE0F']
suit_list = ['diamond', 'club', 'heart', 'spade']
value_list = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']
init_rank_list = [i for i in range(1, 53)]


# a single card
class Card():
    def __init__(self, rank, suit, value):
        self.__rank = rank  # Type: int
        self.__suit = suit  # Type: str
        self.__value = value  # Type: str

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
        for suit in uni_suit_list:
            deck.append(Card(rank, suit, value))
            rank += 1
    return deck


def sort_by_init_rank(cards):
    return cards[0]


def show_cards(cards):
    a = []
    for c in cards:
        a.append(c.get_card())
    return a


# rank: int. Map the rank to the corresponding card. e.g. converter(1) = ♦3
def pattern_converter(rank):
    suit = rank % 4
    if suit == 0:
        suit = 3
    else:
        suit -= 1

    value = (rank - 1) // 4

    pattern = uni_suit_list[suit] + value_list[value]
    return pattern  # str


def unicode_converter(suit):
    c = suit_list.index(suit)
    return uni_suit_list[c]


# Change the format e.g. [3,3,Q,Q,Q] -> [Q,Q,Q,3,3]
def grouping(cards):
    g1 = []
    t1 = cards[0].get_value()

    for c in cards:
        if c.get_value() == t1:
            g1.append(c)

    if len(g1) == 4:
        return g1 + cards[4:5]

    elif len(g1) == 3:
        return g1 + cards[3:5]

    elif len(g1) == 2:
        return cards[2:5] + g1

    else:
        return cards[1:5] + g1


# when a set of cards > 5, check whether it is a 'Straight' / 'Flush' / 'Full House' / 'Quads' / 'Straight flush'.
# return also the rank of the set of cards.
# return Type: (int, int), where 1st: type of combinations, and 2nd: its rank
def check_pattern(cards):
    # ['Straight' / 'Flush' / 'Full House' / 'Quads' / 'Straight flush'] = [1,2,3,4,5]
    # assumption: the cards has been sorted by 'rank'.
    rank = int(cards[4].get_rank())

    straight = \
        (int(cards[0].get_rank()) - 1) // 4 + 1 == (int(cards[1].get_rank()) - 1) // 4 and \
        (int(cards[1].get_rank()) - 1) // 4 + 1 == (int(cards[2].get_rank()) - 1) // 4 and \
        (int(cards[2].get_rank()) - 1) // 4 + 1 == (int(cards[3].get_rank()) - 1) // 4 and \
        (int(cards[3].get_rank()) - 1) // 4 + 1 == (int(cards[4].get_rank()) - 1) // 4

    flush = cards[0].get_suit() == cards[1].get_suit() == cards[2].get_suit() == \
            cards[3].get_suit() == cards[4].get_suit()

    # Straight flush / straight / flush compare: the rank of the largest card.
    if straight and flush:
        return 5, rank

    elif straight:
        return 1, rank

    elif flush:
        return 2, rank

    # cards format: [a,a,a,b,b] or [a,a,a,a,b]
    else:
        cards = grouping(cards)

        # show cards:
        print('-----')
        for c in cards:
            print(c.get_card())
        print('-----')

        same_first_three = cards[0].get_value() == cards[1].get_value() == cards[2].get_value()
        quads = same_first_three and cards[2].get_value() == cards[3].get_value()

        if quads:
            rank = int(cards[3].get_rank())
            return 4, rank

        elif same_first_three:
            if cards[3].get_value() == cards[4].get_value():
                rank = int(cards[2].get_rank())
                return 3, rank

    # default: None of the above
    return 0, 0


def sum_rank(cards):
    s = 0
    for card in cards:
        s += card.get_rank()
    return s


# Determine whether the set of cards is valid. e.g. a pair of '3's is valid. '3' + '4' is not a valid pair comb.
# Compare the set of cards with the current cards. If cards > current_cards: return True
# return Type: (bool, bool), where 1st: valid or not, and 2nd: bigger or not
# cards: list(Card)
def compare(current_cards, cards):
    empty = False

    # The players do not select any cards:
    if not cards:
        return False, False

    # Nothing on the desk:
    if not current_cards:
        c = copy.deepcopy(cards)
        current_cards = c
        empty = True

    valid = len(cards) == len(current_cards)
    print(len(cards))

    greater = sum_rank(cards) >= sum_rank(current_cards)

    if valid:
        # a single card
        if len(cards) == 1:
            pass

        # pairs
        elif len(cards) == 2:
            valid = valid and cards[0].get_value() == cards[1].get_value()

        # Triples
        elif len(cards) == 3:
            valid = valid and cards[0].get_value() == cards[1].get_value() and cards[0].get_value() == cards[2].get_value()

        elif len(cards) == 4 or len(cards) > 5:
            valid = False

        # Five-card hands
        elif len(cards) == 5:
            pattern_of_cards, rank_of_cards = check_pattern(cards)
            print(pattern_of_cards)

            pattern_of_current_cards, rank_of_current_cards = check_pattern(current_cards)

            valid = pattern_of_cards > 0 and pattern_of_cards >= pattern_of_current_cards
            if pattern_of_cards > pattern_of_current_cards or empty:
                greater = True
            else:
                greater = rank_of_cards > rank_of_current_cards

    return valid, greater


# a deck with 52 cards
class Deck():
    def __init__(self, shuf=True):
        self.__deck = get_new_deck()
        self.__cards_set = self.distribute(shuf)

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

    def get_card(self, rank):
        for card in self.__deck:
            if card.get_rank() == rank:
                return card
        return None


# debug:
def test():
    new_deck = Deck(shuf=False)
    card1 = []
    card2 = []

    print('current cards:')
    for i in []:
        c = new_deck.get_card(i)
        print(c.get_card())
        card1.append(c)

    print('-----')
    print('your cards:')
    for i in [1,2,3,4,5]:
        c = new_deck.get_card(i)
        print(c.get_card())
        card2.append(c)

    a, b = compare(card1, card2)
    print(a, b)
# test()