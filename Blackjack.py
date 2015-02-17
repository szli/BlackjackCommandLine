'''
Limitations: 1. Only supports simple win/lose, not care about blackjack winniing situation
2.Does not support split
'''

import random

class Player:
    def clear(self):
        self.cur_bet = 0
        self.lost = False
        self.dd_applied = False
        self.cards = CardGroup()

    def __init__(self, id, cur_money):
        self.id = id
        self.cur_money = cur_money
        self.win_count = 0
        self.is_active = True #If player run out of money it becomes inactive
        self.clear()

    def put_bet(self):
        succ = False
        while not succ:
            try:
                self.cur_bet = int(raw_input("Player %d Put Bet:" % self.id)) #assuming only  integer bets
                succ = True
            except ValueError:
                print "Bet can only be integer!"

        print "Player %d put bet %d" % (self.id, self.cur_bet)
        self.cur_money -= self.cur_bet

    def on_lose(self):
        b = self.cur_bet
        self.cur_bet = 0
        self.lost = True
        print "Player %d lost, cur_money %d" % (self.id, self.cur_money)
        print self.cards
        return b

    def on_win(self):
        self.cur_money += self.cur_bet * 2
        self.win_count += 1
        print "Player %d win, cur_money %d cur_bet %d %s" %(self.id, self.cur_money, self.cur_bet, self.cards)
        return self.cur_bet

    def on_tie(self):
        self.cur_money += self.cur_bet
        print "Player %d tie, cur_money %d %s" % (self.id, self.cur_money, self.cards)

    def get_decision(self):
        print "Player %d, Current Bet %d, Card Status: %s" % (self.id, self.cur_bet, self.cards)
        succ = False
        while not succ:
            user_input = raw_input("Player %d Please take action[H,S,DD]:\n" % self.id)
            if self.dd_applied and user_input !='S':
                print "Double down before, has to Stand"
                continue
            if len(self.cards.cards) == 5 and user_input != 'S':
                print "Already has five cards, cannot Hit or DoubleDown"
                continue
            succ = user_input in ['H','S','DD']
            if not succ: print "Invalid action %s" % user_input
        return user_input

    def on_dd(self):
        self.cur_bet *= 2
        print "Bet increased to %d" %self.cur_bet
        self.cur_money -= self.cur_bet
        self.dd_applied = True

    def receive_cards(self, new_cards):
        print "Player %d Received Cards " % self.id +  ','.join(new_cards)
        return self.cards.add(new_cards)


class CardGroup:
    @staticmethod
    def _get_points(card):
        if card == 'A':
            return 11 #treats A as 11, soft
        if card == '10' or card == 'J' or card == 'Q' or card == 'K':
            return 10
        if ord('9') >= ord(card) >= ord('2'):
            return ord(card) - ord('0')
        raise RuntimeError("Invalid card %s!" % card )


    def clear(self):
        self.cards = []
        self.soft_sum = 0
        self.fav_sum = 0
        self.hasA = False
        self.busted = False

    def __init__(self):
        self.clear()

    def add(self, new_cards):
        if 'A' in new_cards:
            self.hasA = True
        self.cards.extend(new_cards)
        self.soft_sum += sum(map(self._get_points, new_cards))
        self.fav_sum = self.soft_sum - 10 if self.soft_sum > 21 and self.hasA else self.soft_sum
        self.busted = (not self.hasA and self.soft_sum > 21) or (self.hasA and self.soft_sum - 10 > 21)
        return self.busted

    def __repr__(self):
        return "cards = " + ','.join(self.cards) + " sum = " + (str(self.soft_sum) if self.hasA == False else str(self.soft_sum) + "/" + str(self.soft_sum - 10))


class Deck:
    def __init__(self):
        self.cards = []
        self.pos = 0

    def shuffle(self):
        random.shuffle(self.cards)
        self.pos = 0

    def get_cards(self, n):
        self.pos += n
        if self.pos >= len(self.cards):
            raise RuntimeError("No more cards")

        return self.cards[self.pos - n: self.pos]


class SingleDeck(Deck):
    def __init__(self):
        Deck.__init__(self)
        #For simplicity, only care about numbers, ignore color
        self.cards = ['A', '2','3','4','5','6','7','8','9','10','J','Q','K'] * 4
        self.shuffle()


class Dealer:

    def clear(self):
        self.busted = False
        self.dealer_cards.clear()

    def __init__(self, n_players, cur_money):
        self.deck = SingleDeck()
        self.players = [Player(i, 100) for i in range(0, n_players)] #Assuming initial money for each player is 100
        self.dealer_cards = CardGroup()
        self.busted = False
        self.cur_money = cur_money

    def start_game(self):

        iround = 0

        while (True): #Press Ctrl - C to break or one lost all money
            active_players = [p for p in self.players if p.is_active == True]
            if len(active_players) == 0:
                print "All players are out of money!"
                break

            iround += 1
            print "=====Round %d Start=====" % iround
            self.clear()
            map(lambda x: x.clear(), self.players)

            for player in self.players:
                player.put_bet()

            self.dealer_cards.add(self.deck.get_cards(2))
            print "Dealer One Card: %s" % self.dealer_cards.cards[0]

            for player in active_players:
                player.receive_cards(self.deck.get_cards(2))

            #Player Decision
            for player in active_players:
                while True:
                    dec = player.get_decision()
                    bust = False
                    if dec == 'H':
                        bust = player.receive_cards(self.deck.get_cards(1))
                    elif dec=='S':
                        print "Stand"
                        break
                    elif dec=='DD':
                        player.on_dd()
                        bust = player.receive_cards(self.deck.get_cards(1))
                    if bust:
                        print "Busted"
                        self.cur_money += player.on_lose()
                        break

            print "Dealer cards:" + self.dealer_cards.__repr__()
            all_player_lost = reduce(lambda x,y: x and y, map(lambda x: x.lost, active_players))
            if not all_player_lost:
                #Dealer Actions

                while True:
                    if self.dealer_cards.soft_sum > 17: #if <=17 has to draw
                        input = raw_input("Dealer Wants Hit[Y/N]?")
                        if input == 'N':
                            break
                    if len(self.dealer_cards.cards ) == 5:
                        print "Dealer already got five cards, not draw new cards"
                        break
                    bust = self.dealer_cards.add(self.deck.get_cards(1))
                    print "Dealer cards:" + self.dealer_cards.__repr__()
                    if bust:#Dealer bust
                        print "Dealer Busted"
                        for player in active_players:
                            if not player.lost:
                                self.cur_money -= player.on_win()
                        self.busted = True
                        print "Dealer cur_money %d " % self.cur_money
                        break #Done with actions

                if not self.busted:
                    print "Dealer cards: " + self.dealer_cards.__repr__()

                    for player in active_players:
                        if player.lost == False:
                            if player.cards.fav_sum > self.dealer_cards.fav_sum:
                                self.cur_money -= player.on_win()
                            elif player.cards.fav_sum < self.dealer_cards.fav_sum:
                                self.cur_money += player.on_lose()
                            else:
                                player.on_tie()
                            print "Dealer cur_money %d" % self.cur_money
            else:
                 print "All Players are lost, no dealer action needed"

            if self.cur_money <= 0:
                    print "Dealer run out of money!"
                    break

            for p in active_players:
                if p.cur_money <= 0:
                    p.is_active = False
                    print "Player %d is out of money" % p.id


            if iround % 6 == 0:
                print "Round %d, Shuffling" % iround
                self.deck.shuffle()


if __name__ == '__main__':
    dealer = Dealer(2, 10000)
    dealer.start_game()