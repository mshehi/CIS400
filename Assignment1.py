# Megi Shehi
# CIS 400
# Assignment 1

import random  # required to make opponent data

class Game:
    def __init__(self, x, y, z):
        self.options = {a:b for (a,b) in zip([x,y,z],[1,2,3])}  # attach number value to each
        self.playerWins = []  # create list to store player outcomes
        self.compWins = []  # create list to store opponent outcomes

    def input(self, a):  # method to validate input
        try:
            if a in self.options:  # check if input is in valid options dictionary
                return a
        except (TypeError, ValueError):
            pass
        else:
            while a not in self.options:  # loop until input is valid
                print "That's not a valid input! Please type 'Rock', 'Paper', or 'Scissors'. "
                a = raw_input()
            return a

    def opponent(self):
        # randomly generate values from valid options
        autoplays = [x for x in (random.sample(self.options,3))]
        return autoplays

    def compare(self,a,b):
        # translate play into number value
        aval = self.options[a]
        bval = self.options[b]

        # determine round winner
        if aval == bval:
            print "It's a tie!"
            # update wins for player and opponent
            self.playerWins.append(1)
            self.compWins.append(1)
        elif aval == 1:
            if bval == 2:
                print "Your opponent wins this round, better luck next time!"
                self.playerWins.append(0)
                self.compWins.append(1)
            elif bval == 3:
                print "You win this round!"
                self.playerWins.append(1)
                self.compWins.append(0)
        elif aval == 2:
            if bval == 1:
                print "You win this round!"
                self.playerWins.append(1)
                self.compWins.append(0)
            elif bval == 3:
                print "Your opponent wins this round, better luck next time!"
                self.playerWins.append(0)
                self.compWins.append(1)
        elif aval == 3:
            if bval == 1:
                print "Your opponent wins this round, better luck next time!"
                self.playerWins.append(0)
                self.compWins.append(1)
            elif bval == 2:
                print "You win this round!"
                self.playerWins.append(1)
                self.compWins.append(0)

    def winner(self):  # determine overall winner of the game
        # use sum of each list
        sum1 = sum(self.playerWins)
        sum2 = sum(self.playerWins)

        if sum1 == sum2:
            print "It's a tie overall. Thanks for playing!"
        elif sum1 > sum2:
            print "Congratulations, you win! Thanks for playing!"
        else:
            print "Sorry, you lost. Thanks for playing!"

def main():
    g = Game('Rock', 'Paper', 'Scissors')  # create game

    # intro statements
    print "Welcome! We'll be playing Rock, Paper, Scissors today."
    print "Here are the rules of the game: \nRock beats Scissors\nPaper beats Rock\nScissors beats Paper "
    print "You'll have 3 tries to beat your opponent. Best 2 out of 3 wins."
    print "Please type 'Rock', 'Paper', or 'Scissors' to begin."

    o = g.opponent()  # create opponent data
    play1 = g.input(raw_input())  # get user input and check if valid

    # print user and opponent data, and winner for the round
    print "You played " + play1 + " and your opponent played " + o[0]
    g.compare(play1,o[0])

    print "Please enter your selection for Round 2."
    play2 = g.input(raw_input())

    print "You played " + play2 + " and your opponent played " + o[1]
    g.compare(play2, o[1])

    print "Please enter your selection for the final round."
    play3 = g.input(raw_input())

    print "You played " + play3 + " and your opponent played " + o[2]
    g.compare(play3, o[2])

    g.winner()  # find overall winner

if __name__ == "__main__":
    main()