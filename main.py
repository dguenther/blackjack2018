from dealer import Dealer
from humanplayer import HumanPlayer 

def main():
    dealer = Dealer('Dealer', 1000)
    for number in range(2):
        player = HumanPlayer(f'Player {number}', 100)
        dealer.deal_in(player)
    dealer.take_bets()
    while dealer.has_players():
        dealer.deal()
        #dealer.offer_insurance()
        #dealer.offer_surrender()
        dealer.resolve_hands()
        dealer.payout()
        dealer.take_bets()

if __name__ == '__main__':
    main()

