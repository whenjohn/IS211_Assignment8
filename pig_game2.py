#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""week 8"""
import random
import time
import threading

class Die(object):
    """ Object for a Die (single dice)"""
    def __init__(self, sides):
        self.sides = sides
    def roll(self, seed):
        random.seed(seed)
        return random.randint(1,self.sides)

class Player(object):
    def __init__(self):
        self.score = 0

    def updatePlayerScore(self, result):
        self.score += result
        result_message = "holds."
        return (self.score, result_message)

    def returnScore(self):
        return self.score

    def turnDecision(self, current_score, winning_score):
        return input_raw("Enter (r)ole or (h)old: ", ["r","h"])

class ComputerPlayer(Player):
    def __init__(self):
        Player.__init__(self)

    def turnDecision(self, current_score, winning_score):
        time.sleep(2)
        return computerTurnDecision(current_score, winning_score)

def computerTurnDecision(current_score, winning_score):
    if current_score <= (min((winning_score / 4) , (winning_score - current_score))):
        input = "r"
    else:
        input = "h"
    return input

class PlayerFactory(object):
    def startPlayerFactory(self, player_type_list):  # the client
        return self.getPlayer(player_type_list)
    def getPlayer(self, player_type_list): # the creator
        player_list = []
        for player_type in player_type_list:
            if player_type == "h":
                player_list.append((Player()))
            elif player_type == "c":
                player_list.append((ComputerPlayer()))
        return player_list

class Rules(object):
    def __init__(self, winning_score):
        self.winning_score = winning_score
    def hasReachedWinningScoreEndGame(self, current_score):
        game_continue = True
        turn_continue = True
        result_message = None
        if current_score >= self.winning_score:
            game_continue = False
            turn_continue = False
            result_message = "has reached the winning score."
        return (game_continue, turn_continue, result_message)

    def determineWinner(self, all_scores):
        high_score = max(all_scores)
        winning_position = all_scores.index(high_score)
        result_message = "Player {} has won the game with a score of {}.".format((winning_position + 1), high_score)
        return (result_message)

    def rollResult(self, roll_value, incoming_score):
        result_score = incoming_score + roll_value
        turn_continue = True
        result_message = "Rolled {}".format(roll_value)
        return (result_score, turn_continue, result_message)

class PigRules(Rules):
    def __init__(self, winning_score):
        Rules.__init__(self, winning_score)
    def rollResult(self, roll_value, incoming_score):
        pig_factory = PigRulesFactory()
        return pig_factory.startRulesFactory(roll_value, incoming_score)

class PigRulesFactory(object):
    def startRulesFactory(self, roll_value, incoming_score):
        return self.getRulesLogic(roll_value, incoming_score)
    def getRulesLogic(self, roll_value, incoming_score):
        if roll_value == 1:
            result_score = 0
            turn_continue = False
            result_message = "rolled a 1. End turn."
        else:
            result_score = incoming_score + roll_value
            turn_continue = True
            result_message = "rolled a {}".format(roll_value)
        return (result_score, turn_continue, result_message)

class GameTypeFactory(object):
    def startGameTypeFactory(self, type, sides_of_die, winning_score, timer):
        return self.getGameType(type, sides_of_die, winning_score, timer)

    def getGameType(self, type, sides_of_die, winning_score, timer):
        if type == 'r':
            return Game(sides_of_die, winning_score, timer)
        if type == 't':
            return TimedGameProxy(sides_of_die, winning_score, timer)

class Game(object):
    """ Object for the game"""
    def __init__(self, sides, winning_score, timer=None):
        self.game_die = Die(sides)
        self.game_rules = PigRules(winning_score)
        self.winning_score = winning_score
        self.game_continue = True
        self.turn_continue = True

    def roll(self, seed):
        return self.game_die.roll(seed)

    def createPlayerList(self, incoming_players):
        self.game_players = []
        factory = PlayerFactory()
        self.game_players = factory.startPlayerFactory(incoming_players)

    def getRollResult(self, roll_value, incoming_score):
        return self.game_rules.rollResult(roll_value, incoming_score)

    def getHoldResult(self, player_position, result):
        turn_continue = True
        (result_score, result_message) = self.game_players[player_position].updatePlayerScore(result)
        (game_continue, turn_continue, result_message1) = self.game_rules.hasReachedWinningScoreEndGame(result_score)
        if game_continue == False: result_message = result_message1
        return (game_continue, turn_continue, result_score, result_message)

    def determineGameWinner(self):
        return self.game_rules.determineWinner(self.returnAllPlayerScore())

    def returnPlayerScore(self, player_position):
        return self.game_players[player_position].returnScore()

    def returnAllPlayerScore(self):
        all_scores = []
        for position in range (len(self.game_players)):
            all_scores.append( self.game_players[position].returnScore() )
        return all_scores

    def playerTurnDecision(self, player_position, current_score):
        return self.game_players[player_position].turnDecision(current_score, self.winning_score)

    def gameLoop(self):
        updated_score = 0

        # Game Loop
        while self.game_continue:
            # cycle between players
            for player_position in range (len(self.game_players)):
                # Clear values for each turn
                temp_score = 0

                # reset turn unless game has ended
                if self.game_continue:
                    self.turn_continue = True

                # Turns loop
                while self.turn_continue:
                    print "\nPlayer {} Turn".format(player_position + 1)

                    user_input = self.playerTurnDecision(player_position, temp_score)

                    if user_input == "r" and ( self.game_continue is True and self.turn_continue is True ):
                        (temp_score, self.turn_continue, result_message) = self.getRollResult(self.roll(time.time()), temp_score)
                        print "Player {} {}".format((player_position + 1), result_message)

                    elif user_input == "h" and ( self.game_continue is True and self.turn_continue is True ):
                        (self.game_continue, self.turn_continue, updated_score, result_message) = self.getHoldResult(player_position, temp_score)
                        print "Player {} {}".format((player_position + 1), result_message)
                        print "\nThe score is ",self.returnAllPlayerScore()
                        break

                    else:
                        break

class TimedGameProxy(Game):
    def __init__(self, sides, winning_score, timer):
        self.timer_duration = timer
        Game.__init__(self, sides, winning_score)

    def gameLoop(self):
        print "Game timer: {}".format(self.timer_duration)
        timer = threading.Timer(self.timer_duration, self.timerCompleteStopGame )
        timer.start()
        Game.gameLoop(self)
        if self.game_continue is False and self.turn_continue is False:
            timer.cancel()

    def timerCompleteStopGame(self):
        print "\nTimer has ended.\n"
        self.game_continue = False
        self.turn_continue = False
        Game.gameLoop(self)

def input_int(question):
    """Function to ask a int question

    Args:
        question (string): the question to ask user

    Attributes:

    Returns:
        Returns int from user
    Examples:
    """
    while True:
        try:
            value = int(input(question))
        except (SyntaxError, NameError) as exception:
            print("Invalid entry. Try again.")
            continue

        if value <= 0:
            print("Invalid entry. Try again.")
            continue
        else:
            break

    return value

def input_raw(question, answers):
    """Function to ask a question recives string response

    Args:
        question (string): the question to ask user
        answers (list): acceptable answers that

    Attributes:
        match (bool): If match found

    Returns:
        Returns accepted input from user
    Examples:
    """
    match = False

    while match is False:
        input = raw_input(question)

        for answer in answers:
            if  input == answer:
                match = True
                break

        if match is False:
            print "Wrong entry. Please enter",answers

    return input

def main():
    """Main function that runs at start of program.

    Args:

    Attributes:
        winning_score (int): the score to determine a winner
        counter (int): counter
        game_list (list): a list of games
        sides_of_die (int): num of sides of die
        player_type_list (list) = list of types of players
        timer (float) = timer of game

    Returns:

    Examples:
        >>> $ python pig_game.py
        >>> How many games do you want to play?: 1
        Starting Game 1

        Player 1 Turn
        Enter (r)ole or (h)old:r
    """
    # Game Configs
    sides_of_die = 6
    winning_score = 20
    game_list = []
    player_type_list = []
    timer = 30.0

    # User input to set up games
    num_of_games = input_int("How many games do you want to play?: ")
    for count_a in range(num_of_games):
        player_type_list = [] # reset list
        game_type = input_raw("\nFor Game {}: Will it be a (r)egular game or (t)imed game? ".format((count_a + 1)), ["r","t"])
        num_of_players = input_int("\nFor Game {}: How many players? ".format((count_a + 1)))
        for count_b in range(num_of_players):
            player_type_list.append(input_raw("For Game {}: Is player {} (h)uman or (c)omputer? ".format((count_a + 1), (count_b + 1)), ["h","c"]))
        game_factory = GameTypeFactory()
        game_list.append((game_factory.startGameTypeFactory(game_type, sides_of_die, winning_score, timer), (player_type_list)))

    # Play all games.
    counter = 1
    for games, player_type_list in game_list:
        print "\nStarting Game {}. First to {} wins! ".format(counter, winning_score)
        games.createPlayerList(player_type_list)
        games.gameLoop()
        counter += 1
        print games.determineGameWinner()
    print "\nCompleted all the games!\n"


# Run main if file direcrly executed
if __name__ == '__main__':
    main()
