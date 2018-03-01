from player import Player
from shoe import Shoe
from hand import Hand

class Dealer(Player):

    def __init__(self, name, money):
        super().__init__(name, money)
        self.shoe = Shoe()
        self.players = []
        # Holds bets before hands have been dealt
        # We could make this a dictionary with the player's name as the key,
        # but that assumes the player names are unique. Better solution would
        # probably be to set bets on the Player object
        self.playerBets = []

#region Dealer-specific methods

    def deal_in(self, player):
        """Add a player to the dealer's table"""
        self.players.append(player)

    def has_players(self):
        """Returns true if the dealer is dealing to at least 1 player"""
        return len(self.players) > 0

    def take_bets(self):
        """Ask all players how much they want to bet. Removes them from the table if they bet -1"""
        for player in self.players:
            bet = player.bet_or_leave()
            # Add each player's bet to a list of bets
            self.playerBets.append(bet)
        # Filter out players if they bet -1
        self.players = [p for i, p in enumerate(self.players) if self.playerBets[i] != -1]
        # Remove the -1 bets from the list of bets
        self.playerBets = [b for b in self.playerBets if b != -1]

    def deal(self):
        """Deal out hands to the players. Assumes we've taken bets"""
        # Shuffle the shoe if it needs it
        if (self.shoe.should_shuffle()):
            self.shoe.shuffle()
        
        # Deal out cards to the players
        for index, player in enumerate(self.players):
            bet = self.playerBets[index]
            # Don't deal a hand if the player bet 0
            if bet > 0:
                player.rake_out(bet)
                hand = Hand(bet)
                for _ in range(2):
                    hand.hit(self.shoe.draw().flip())
                player.add_hand(hand)
        
        # Clear out playerBets, all bets are on hands now
        self.playerBets = []

        # Deal out cards to the dealer
        dealerHand = Hand(0)
        for _ in range(2):
            dealerHand.hit(self.shoe.draw().flip())
        # Give the dealer the hand
        self.add_hand(dealerHand)
        
    def resolve_hands(self):
        dealerHand = self.hands[0]
        dealerShowing = dealerHand[-1]
        for player in self.players:
            for hand in player.hands:
                while hand.can_hit():
                    choice, bet = player.play(hand, dealerShowing)
                    if (choice == 's'):
                        hand.stand()
                    if (choice == 'h'):
                        hand.hit(self.shoe.draw().flip())
                    if (choice == 'd'):
                        player.rake_out(bet)
                        hand.double_down(self.shoe.draw().flip(), bet)
                    if (choice == 'p'):
                        player.rake_out(hand.bet)
                        splitHand = Hand(hand.bet)
                        card = hand.split()
                        splitHand.hit(card)
                        splitHand.hit(self.shoe.draw().flip())
                        player.add_hand(splitHand)
                        hand.hit(self.shoe.draw().flip())

                print(f"{player.name} finishes with {hand}")
                        

        # Now that the players have played, the dealer needs to play
        print("Let's see what the dealer has...")
        print(f"{self.name} flips their card, showing {dealerHand}")
        while dealerHand.can_hit():
            self.play(dealerHand, dealerShowing)
        print(f"{self.name} stands with {dealerHand}")

    def payout(self):
        print("Time to pay out!")
        dealerHand = self.hands[0]
        for player in self.players:
            for hand in player.hands:
                # If the player busts, they lose
                if hand.isBusted:
                    print(f"{player.name} busts, losing ${hand.bet:,.2f}.")
                    self.rake_in(hand.bet)
                # If the player's hand is worth less than dealer, they lose
                elif hand < dealerHand:
                    print(f"{player.name} lost to the dealer, losing ${hand.bet:,.2f}.")
                    self.rake_in(hand.bet)
                # If the hands are equal, the player gets their bet back
                elif hand == dealerHand:
                    print(f"{player.name} pushed, returning their bet of ${hand.bet:,.2f}.")
                    player.rake_in(hand.bet)
                # if player has blackjack and dealer doesn't (checked in == case), they win
                elif hand.isBlackJack:
                    # Blackjack pays 3:2
                    print(f"Blackjack! {player.name} wins ${hand.bet * 1.5:,.2f}.")
                    player.rake_in(hand.bet + hand.bet * 1.5)
                # If the player's hand is worth more than dealer, they win
                elif hand > dealerHand:
                    # Winning pays 1:1
                    print(f"{player.name} beat the dealer, winning ${hand.bet:,.2f}.")
                    player.rake_in(hand.bet + hand.bet)
                else:
                    raise NotImplementedError(f'Unchecked condition in payout. Player hand: {hand} Dealer: {dealerHand}.')
            player._hands = []
            self._hands = []

        # Remove players that run out of money
        for player in self.players:
            if player.money <= 0:
                print(f"{player.name} is out of cash. Thanks for playing!")
        self.players = [p for p in self.players if p.money > 0]

#endregion

    def play(self, hand, dealerShowing):
        # Dealer hits on soft 17
        if (hand.hard_value() >= 17):
            hand.stand()
        else:
            hand.hit(self.shoe.draw().flip())

