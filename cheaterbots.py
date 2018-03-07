from player import Player
from hand import Hand
import sys
from copy import deepcopy
from functools import reduce 
import operator

import unittest
from shoe import Shoe
from table import Table
from dealer import Dealer

class CheaterBotOne(Player):
    """
    A cheating programmer bot. The goal is to cheat by observing game state but not
    modifying it.
    """

    def __init__(self, money):
        super().__init__('Cheater 1', money)
        self.cardDistributionOrderKnown = False
        self.cardDistributionOrder = {
            'dealer': [],
            'self': [],
        }
        self.shoe = None

    def find_type_contains(self, typestring):
        level = 1
        shoe = None
        while shoe == None:
            f = sys._getframe(level)
            for c in f.f_locals:
                if (str(type(f.f_locals[c])).lower().find(typestring) != -1):
                    shoe = f.f_locals[c]
            level += 1
        return shoe

    def find_shoe(self):
        """Search up the stack looking for the shoe the dealer is using"""
        dealer = self.find_type_contains('dealer')
        return dealer._shoe

    def find_card_in_shoe(self, shoe, card, distance = 4):
        for i in range(distance):
            if self.cards_are_equal(shoe[i], card):
                return i
            if self.cards_are_equal(shoe[-(i+1)], card):
                return -(i + 1)
        return None

    def cards_are_equal(self, card1, card2):
        return repr(card1) == repr(card2)

    def bet_or_leave(self):
        shoe = self.find_shoe()
        if not self.cardDistributionOrderKnown:
            # If we don't know the card distribution order, we'll copy the shoe,
            # bet something small, then see who ends up with which cards
            self.shoe = deepcopy(shoe)
            bet = 1
        else:
            dealerHand = Hand(0)
            dealerCard1 = shoe[self.cardDistributionOrder['dealer'][0]]
            dealerCard2 = shoe[self.cardDistributionOrder['dealer'][1]]
            dealerHand.hit(dealerCard1.flip())
            dealerHand.hit(dealerCard2.flip())
            selfHand = Hand(0)
            selfCard1 = shoe[self.cardDistributionOrder['self'][0]]
            selfCard2 = shoe[self.cardDistributionOrder['self'][1]]
            selfHand.hit(selfCard1.flip())
            selfHand.hit(selfCard2.flip())
            # Bet everything if we're guaranteed to win, else sit out
            if dealerHand.value() >= 17 and selfHand.value() > dealerHand.value():
                bet = self.money
            else:
                bet = 0
            # Put the cards back to the way they were
            dealerCard1.flip()
            dealerCard2.flip()
            selfCard1.flip()
            selfCard2.flip()
        return bet

    def wants_insurance(self):
       return False

    def play(self, hand, dealerShowing):
        if not self.cardDistributionOrderKnown:
            dealer = self.find_type_contains('dealer')
            self.cardDistributionOrder['dealer'] = []
            for card in dealer.get_hands()[0]:
                index = self.find_card_in_shoe(self.shoe, card)
                self.cardDistributionOrder['dealer'].append(index)
            self.cardDistributionOrder['self'] = []
            for card in self.get_hands()[0]:
                index = self.find_card_in_shoe(self.shoe, card)
                self.cardDistributionOrder['self'].append(index)
            nums = self.cardDistributionOrder['self'] + self.cardDistributionOrder['dealer']
            totalcount = reduce(
                lambda acc, cur: acc + 1 if cur >= 0 else acc - 1,
            nums, 0)
            # If we aren't able to find our cards in the first 4 or last 4,
            # we're not certain of the card distribution order yet.
            if (abs(totalcount) == len(nums)):
                self.cardDistributionOrderKnown = True
                self.shoe = None
        # Always stand, since we'll only bet in situations we're guaranteed to win
        # without having to hit
        return 's', None

        # if hand.value() < 17:
        #     choice = 'h' #hit
        # else:
        #     choice = 's' #stand
        # return choice, None

class CheaterTests(unittest.TestCase):
    # def test_distribution_order(self):
    #     table = Table(doubleOn=[9,10,11])
    #     dealer = Dealer('Dealer', 1000000)
    #     dealer.sit(table)
    #     bot = CheaterBotOne(100)
    #     bot.sit(table)
    #     dealer.take_bets()
    #     self.assertIsNotNone(bot.shoe)
    #     print(bot.shoe)
    #     print(dealer._shoe)
    #     dealer.deal()
    #     print(bot.get_hands())
    #     print(dealer.get_hands())
    #     print(dealer._shoe)
    #     dealer.play_hands()
    #     self.assertTrue(bot.cardDistributionOrderKnown)
    #     self.assertEqual(bot.cardDistributionOrder['self'][0], -1)
    #     self.assertEqual(bot.cardDistributionOrder['self'][1], -2)
    #     self.assertEqual(bot.cardDistributionOrder['dealer'][0], -3)
    #     self.assertEqual(bot.cardDistributionOrder['dealer'][1], -4)

    def test_turn_2(self):
        table = Table(doubleOn=[9,10,11])
        dealer = Dealer('Dealer', 1000000)
        dealer.sit(table)
        bot = CheaterBotOne(100)
        bot.sit(table)
        dealer.take_bets()
        dealer.deal()
        dealer.play_hands()
        dealer.play_own_hand()
        dealer.payout_hands()
        # Round 2
        dealer.take_bets()
        print(dealer._shoe)
        dealer.deal()
        dealer.play_hands()
        dealer.play_own_hand()
        dealer.payout_hands()

if __name__ == '__main__':
    unittest.main()
