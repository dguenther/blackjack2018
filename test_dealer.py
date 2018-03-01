import unittest
from unittest.mock import MagicMock
from hand import Hand
from card import Card
from player import Player
from dealer import Dealer

class DealerTests(unittest.TestCase):

    def deal_in_player(self, dealer):
        player = Player('name', 100)
        dealer.deal_in(player)
        self.assertEqual(dealer.players[-1], player)
        return player

    def deal_hand(self, dealer, bet, *cards):
        player = self.deal_in_player(dealer)
        player.bet_or_leave = MagicMock(return_value=bet)
        dealer.take_bets()
        dealer.deal()
        hand = Hand(bet)
        for card in cards:
            hand.hit(card)
        player.hands[0] = hand
        return player

    def set_dealer_hand(self, dealer, card1, card2):
        hand = Hand(0)
        hand.hit(card1)
        hand.hit(card2)
        dealer.hands[0] = hand

    def test_stands_on_hard_17(self):
        dealer = Dealer('test', 100)
        hand = Hand(100)
        hand.hit(Card('king', 'diamonds').flip())
        hand.hit(Card('7', 'diamonds').flip())
        dealer.play(hand, None)
        self.assertTrue(hand.isStanding)

    def test_hits_on_soft_17(self):
        dealer = Dealer('test', 100)
        hand = Hand(100)
        hand.hit(Card('ace', 'diamonds').flip())
        hand.hit(Card('7', 'diamonds').flip())
        dealer.play(hand, None)
        self.assertEqual(len(hand), 3)
        self.assertFalse(hand.isStanding)

    def test_deal_in(self):
        dealer = Dealer('test', 100)
        player = Player('player', 100)
        dealer.deal_in(player)
        self.assertEqual(len(dealer.players), 1)
        self.assertEqual(dealer.players[0], player)

    def test_has_players(self):
        dealer = Dealer('test', 100)
        self.assertFalse(dealer.has_players())
        player = Player('player', 100)
        dealer.deal_in(player)
        self.assertTrue(dealer.has_players())

    def test_leave_table(self):
        dealer = Dealer('test', 100)
        player = Player('player', 100)
        lPlayer = Player('leavingPlayer', 100)
        dealer.deal_in(player)
        dealer.deal_in(lPlayer)
        self.assertEqual(len(dealer.players), 2)
        player.bet_or_leave = MagicMock(return_value=50)
        lPlayer.bet_or_leave = MagicMock(return_value=-1)
        dealer.take_bets()
        self.assertEqual(len(dealer.players), 1)
        self.assertEqual(dealer.players[0], player)
        self.assertEqual(len(dealer.playerBets), 1)
        self.assertEqual(dealer.playerBets[0], 50)

    def test_shuffles_if_necessary(self):
        dealer = Dealer('test', 100)
        dealer.shoe.should_shuffle = MagicMock(return_value=True)
        dealer.shoe.shuffle = MagicMock()
        dealer.deal()
        dealer.shoe.shuffle.assert_called()

    def test_doesnt_deal_when_0_bet(self):
        dealer = Dealer('test', 100)
        player = self.deal_in_player(dealer)
        player.bet_or_leave = MagicMock(return_value=0)
        dealer.take_bets()
        player.add_hand = MagicMock()
        dealer.deal()
        player.add_hand.assert_not_called()

    def test_deals_when_nonzero_bet(self):
        dealer = Dealer('test', 100)
        player = self.deal_in_player(dealer)
        player.bet_or_leave = MagicMock(return_value=50)
        dealer.take_bets()
        player.rake_out = MagicMock()
        player.add_hand = MagicMock()
        dealer.deal()
        player.rake_out.assert_called()
        player.add_hand.assert_called_once()
        # Expect add_hand to have been called with a hand
        # that has two cards
        hand = player.add_hand.call_args[0][0]
        self.assertEqual(len(hand), 2)

    def test_deals_to_self(self):
        dealer = Dealer('test', 100)
        dealer.add_hand = MagicMock()
        dealer.deal()
        # Expect add_hand to have been called with a hand
        # that has two cards
        hand = dealer.add_hand.call_args[0][0]
        self.assertEqual(len(hand), 2)

    def test_handles_stand(self):
        dealer = Dealer('test', 100)
        firstCard = Card('king', 'diamonds').flip()
        secondCard = Card('king', 'spades').flip()
        player = self.deal_hand(dealer, 50, firstCard, secondCard)
        hand = player.hands[0]
        hand.stand = MagicMock()
        hand.can_hit = MagicMock(side_effect=[True, False])
        player.play = MagicMock(return_value=('s', None))
        dealer.resolve_hands()
        hand.stand.assert_called_once()

    def test_handles_hit(self):
        dealer = Dealer('test', 100)
        firstCard = Card('king', 'diamonds').flip()
        secondCard = Card('king', 'spades').flip()
        player = self.deal_hand(dealer, 50, firstCard, secondCard)
        hand = player.hands[0]
        hand.hit = MagicMock()
        hand.can_hit = MagicMock(side_effect=[True, False])
        player.play = MagicMock(return_value=('h', None))
        dealer.resolve_hands()
        hand.hit.assert_called_once()

    def test_handles_double(self):
        dealer = Dealer('test', 100)
        firstCard = Card('king', 'diamonds').flip()
        secondCard = Card('king', 'spades').flip()
        player = self.deal_hand(dealer, 50, firstCard, secondCard)
        hand = player.hands[0]
        hand.double_down = MagicMock()
        hand.can_hit = MagicMock(side_effect=[True, False])
        player.play = MagicMock(return_value=('d', 10))
        dealer.resolve_hands()
        hand.double_down.assert_called_once()
        # Calls double down with the additional bet
        self.assertEqual(hand.double_down.call_args[0][1], 10)

    def test_handles_split(self):
        dealer = Dealer('test', 100)
        firstCard = Card('king', 'diamonds').flip()
        secondCard = Card('king', 'spades').flip()
        player = self.deal_hand(dealer, 50, firstCard, secondCard)
        player.play = MagicMock(side_effect=[('p', None), ('s', None), ('s', None)])
        dealer.resolve_hands()
        # Player should have 2 hands
        self.assertEqual(len(player.hands), 2)
        # Player should have played both hands
        self.assertEqual(player.play.call_count, 3)
        # Dealer should have taken money from player
        self.assertEqual(player.money, 0)
        firstHand = player.hands[0]
        # The first hand should be split
        self.assertTrue(firstHand.isSplit)
        # The first card of each hand should be cards from the original hand
        self.assertEqual(firstHand[0], firstCard)
        self.assertEqual(player.hands[1][0], secondCard)
        # Player should have the same bet and be standing on both hands
        for hand in player.hands:
            self.assertEqual(hand.bet, 50)
            self.assertTrue(hand.isStanding)
    
    def test_payout_losing(self):
        dealer = Dealer('test', 100)
        firstCard = Card('2', 'diamonds').flip()
        secondCard = Card('2', 'spades').flip()
        self.deal_hand(dealer, 50, firstCard, secondCard)
        firstCard = Card('10', 'diamonds').flip()
        secondCard = Card('10', 'spades').flip()
        self.set_dealer_hand(dealer, firstCard, secondCard)
        dealer.rake_in = MagicMock()
        dealer.payout()
        dealer.rake_in.assert_called_once_with(50)

    def test_payout_busted(self):
        dealer = Dealer('test', 100)
        firstCard = Card('10', 'diamonds').flip()
        secondCard = Card('10', 'spades').flip()
        thirdCard = Card('10', 'spades').flip()
        self.deal_hand(dealer, 50, firstCard, secondCard, thirdCard)
        firstCard = Card('10', 'diamonds').flip()
        secondCard = Card('10', 'spades').flip()
        self.set_dealer_hand(dealer, firstCard, secondCard)
        dealer.rake_in = MagicMock()
        dealer.payout()
        dealer.rake_in.assert_called_once_with(50)

    def test_payout_winning(self):
        dealer = Dealer('test', 100)
        firstCard = Card('10', 'diamonds').flip()
        secondCard = Card('10', 'spades').flip()
        player = self.deal_hand(dealer, 50, firstCard, secondCard)
        firstCard = Card('9', 'diamonds').flip()
        secondCard = Card('9', 'spades').flip()
        self.set_dealer_hand(dealer, firstCard, secondCard)
        player.rake_in = MagicMock()
        dealer.payout()
        player.rake_in.assert_called_once_with(100)

    def test_payout_push(self):
        dealer = Dealer('test', 100)
        firstCard = Card('10', 'diamonds').flip()
        secondCard = Card('10', 'spades').flip()
        player = self.deal_hand(dealer, 50, firstCard, secondCard)
        firstCard = Card('10', 'diamonds').flip()
        secondCard = Card('10', 'spades').flip()
        self.set_dealer_hand(dealer, firstCard, secondCard)
        player.rake_in = MagicMock()
        dealer.payout()
        player.rake_in.assert_called_once_with(50)

    def test_payout_blackjack(self):
        dealer = Dealer('test', 100)
        firstCard = Card('10', 'diamonds').flip()
        secondCard = Card('ace', 'spades').flip()
        player = self.deal_hand(dealer, 50, firstCard, secondCard)
        firstCard = Card('10', 'diamonds').flip()
        secondCard = Card('10', 'spades').flip()
        self.set_dealer_hand(dealer, firstCard, secondCard)
        player.rake_in = MagicMock()
        dealer.payout()
        player.rake_in.assert_called_once_with(125)

    def test_hands_cleared_after_payout(self):
        dealer = Dealer('test', 100)
        firstCard = Card('10', 'diamonds').flip()
        secondCard = Card('ace', 'spades').flip()
        player = self.deal_hand(dealer, 50, firstCard, secondCard)
        firstCard = Card('10', 'diamonds').flip()
        secondCard = Card('10', 'spades').flip()
        self.set_dealer_hand(dealer, firstCard, secondCard)
        dealer.payout()
        self.assertEqual(len(player.hands), 0)
        self.assertEqual(len(dealer.hands), 0)

if __name__ == '__main__':
    unittest.main()