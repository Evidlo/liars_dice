#!/bin/python
# Evan Widloski - 2015-10-09
# Liar's Dice simulator control program - bots are defined as single
# Functions under the section ### BOTS ###

from random import randint
from itertools import cycle
'''
BOT INPUT EXAMPLE

round : {'players':[
        {'bet':(3,1),'num_die':6},
        {'bet':(4,4),'num_die':5},
        {'bet':None,'num_die':6},
        'previous_id':1,
        'previous_bet':(4,4),
        'current_id':2,
        'your_id':2,
        'your_rolls':[6,5,4,3,2,1],
        'game_over':0
        }

player 1 bets three 1's and has 6 dice
player 2 bets four 4's and has 5 dice
player 3 hasn't bet and has 6 dice
your id is 2

round : {'players':[
        {'bet':(3,1),'num_die':6,'rolls':[1,2,3,4,5,6]},
        {'bet':(4,4),'num_die':5,'rolls':[5,5,5,5,5]},
        {'bet':None,'num_die':6,'rolls:[6,5,4,3,2,1]'},
        'previous_id':1,
        'previous_bet':(4,4),
        'current_id':2,
        'your_id':2,
        'your_rolls':[6,5,4,3,2,1],
        'game_over':1
        }

the round is over, player rolls are revealed


you should return a tuple ('number of dice','value') to bet, 'bluff' or 'spot on'
your response is ignored when it is not your turn
'''

### BOTS ###

def crapbot(game):
    #check if its our turn
    if game['current_id'] == game['your_id']:
        print 'im player {0}'.format(game['your_id'])
        print 'my dice: ',game['your_rolls']

        #if were player 1, always call spot on
        if game['your_id'] == 1:
            return 'spot on'

        #check if were not the first to bet
        if game['previous_bet']:
            #if the previous bet was over 7 die, call a bluff.  otherwise, give a bet
            if game['previous_bet'][0] > 7:
                return 'bluff'
            number = game['previous_bet'][0] + 1
            value = 5
            return (number, value)

        number = 5
        value = 5
        return (number, value)

    #its not our turn
    return


#define the list of players here
bot_funcs = [crapbot, crapbot, crapbot]

### GAME ###

#player class which stores their info and function to call when they are run
class Player(object):
    def __init__(self,function,id):
        self.function = function
        self.bets = []
        self.num_die = 6
        self.rolls = []
        self.id = id

#get a list of active players
def active_players(players):
    return [player for player in players if player.num_die > 0]


#cound the number of occurences of each value rolled
def count_rolls(players):
    rolls_sum = [0,0,0,0,0,0]
    for player in players:
        for roll in player.rolls:
            rolls_sum[roll - 1] += 1

    return rolls_sum

#update the round
def generate_round(players,current_player,player,previous_player):
    round = {'players':[],'previous_id':None,'previous_bet':None,'current_id':None,'your_id':None,'your_roll':[]}
    round['your_id'] = player.id
    round['your_rolls'] = player.rolls
    for player in players:
        round['players'].append({'id':player.id,'bet':None,'num_die':player.num_die})
    round['current_id'] = current_player.id
    if previous_player:
        round['previous_id'] = previous_player.id
        round['previous_bet'] = previous_player.bets[-1]
    else:
        round['previous_id'] = None
        round['previous_bet'] = None
    return round


#instantiate list of player objects
players = [Player(bot_func,id) for id,bot_func in enumerate(bot_funcs)]

game_cycle = iter(cycle(players))
#game loop
while len(active_players(players)) > 1:
    print "\n### NEW ROUND - {0}\n".format([player.num_die for player in players])
    previous_player = None

    #randomly roll for all players
    for player in players:
        player.rolls = [randint(1,6) for _ in range(player.num_die)]

    #round loop
    for current_player in game_cycle:

        #send round info to all players, retrieve bet from current player
        for player in players:
            round = generate_round(players,current_player,player,previous_player)

            #verify the response from the current player
            if current_player == player:
                #check if the player is in the game
                if current_player.num_die >= 1:
                    response = player.function(round)
                    #validate player response
                    if response not in ['spot on','bluff'] and type(response) != tuple:
                        raise ValueError('Player {0} gave an invalid bet:{1}'.format(current_player.id, response))
                else:
                    response = None


            #for the other players, just send them the round info, but don't look at their response
            else:
                player.function(round)

        #record the player's bet
        current_player.bets.append(response)

        #evaluate current players bet - three kinds of bets
        if response == 'bluff':
            if not previous_player:
                raise ValueError('The first player tried to call bluff!')
            print "### Player {0} called a bluff".format(current_player.id)
            bet = previous_player.bets[-1]
            if count_rolls(players)[bet[1] - 1] >= bet[0]:
                print "The bluff was False!"
                current_player.num_die -= 1
            else:
                print "The bluff was True!"
                previous_player.num_die -= 1
            break

        elif response == 'spot on':
            if not previous_player:
                raise ValueError('The first player tried to call spot on!')
            print "### Player {0} called a spot on".format(current_player.id)
            bet = previous_player.bets[-1]
            if count_rolls(players)[bet[1] - 1] == bet[0]:
                print "The spot on was True!"
                for player in players:
                    if player != current_player:
                        player.num_die -= 1
            else:
                print "The spot on was False!"
                current_player.num_die -= 1
            break

        elif type(response) == tuple:
            print "### Player {0} bet {1}".format(current_player.id,response)
            if previous_player:
                previous_bet = previous_player.bets[-1][0]
                if (response[0] <= previous_bet):
                    raise ValueError('Player {0} did not raise the number of die bet! He bet {1} and the previous player bet {2}'.format(current_player.id, response[0], previous_bet))


        #set the previous player (but don't count non-active players)
        if current_player.num_die > 0:
            previous_player = current_player

    print "\nDice total:",count_rolls(players)

print "\n### WINNER - Player {0}".format(active_players(players)[0].id)

#try putting bet tuple into a dict so it can be accessed like player1.bets.value
#have the bot function return a similar object (response.value)

#implement game_over
