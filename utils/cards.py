import enum
import numpy as np
import random
from game import Game
DECK_SIZE = 52
class Deck:
    def __init__(self):
        self.reset_deck()
        self.suits = ("Spades", "Diamonds", "Clubs", "Hearts")
        self.max_size = DECK_SIZE

    def reset_deck(self):
        self.deck = np.ones(DECK_SIZE)
        self.count = DECK_SIZE
        self.remaining = []
        for i in range(DECK_SIZE):
            self.remaining.append(i)
    def draw_cards(self, n):
        if n > self.count:
            return None
        cards = []
        for i in range(n):
            index = random.randint(0,size)
            card = self.remaining.pop(index)
            self.deck[card] -= 1
            self.count -= 1
            cards.append(card)
        return cards
    def add_cards(self, cards):
        num_added = 0
        for card in cards:
            if card > self.max_size:
                continue
            self.deck[card] += 1
            self.remaining.append(card)
            num_added += 1
        return num_added
    def card_value(self, card):
        value = card % 13 + 1
    def get_deck(self):
        return self.deck
    def get_current_size(self):
        return self.count
    
class Blackjack(Game):
    def __init__(self, id):
        super().__init__(id)
        self.reset()
    def reset(self):
        self.state = 0
        self.player_hand = []
        self.dealer_hand = []
        self.player_total = 0
        self.dealer_total = 0
        self.deck = Deck()
    def next_state(self):
        pass
    def game_state(self):
        pass
    def hit(self):
        pass
    def stand(self):
        pass
    def start_game(self):
        pass



            
            
                

            
