'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
import eval7
import random
import pandas as pd


class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        # self.strong_hole = False
        # singles = []
        # pairs = []
        # toak = []
        self.board_cards = []
        self.final_action = None
        calculated_df = pd.read_csv('hole_strengths.csv')
        holes = calculated_df.Holes #the columns of our spreadsheet
        strengths = calculated_df.Strengths
        self.starting_strengths = dict(zip(holes, strengths)) #convert to a dictionary, O(1) lookup time!

        

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        my_cards = round_state.hands[active]  # your cards
        big_blind = bool(active)  # True if you are the big blind    
        print('Round Number: #' + str(round_num))
        pass

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        street = previous_state.street  # int of street representing when this round ended
        my_cards = previous_state.hands[active]  # your cards
        opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed

        # avail_cards = my_cards + board_cards
        # hand = [eval7.Card(card) for card in avail_cards]
        # index = eval7.evaluate(hand)
        # handtype = eval7.handtype(index)
        # print(handtype)
        print('The final action was:', self.final_action)
        print(my_cards) #, 'hand =', eval7.evaluate)
        print(opp_cards)
        print(self.board_cards)
        if my_delta > 0:
            print('You won this round')
        elif my_delta < 0:
            print('You lost this round')
        else:
            print('You tied this round')
        print()

    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # int representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        self.board_cards = board_cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot
        
        # if RaiseAction in legal_actions:
        #    min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
        #    min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
        #    max_cost = max_raise - my_pip  # the cost of a maximum bet/raise

        min_raise, max_raise = round_state.raise_bounds()
        
        my_action = None

        pot_total = my_contribution + opp_contribution

        if street < 3:
            raise_amount = int(my_pip + continue_cost + 0.4 * (pot_total + continue_cost))
        else:
            raise_amount = int(my_pip + continue_cost + 0.75 * (pot_total + continue_cost))

        raise_amount = max([min_raise, raise_amount])

        raise_cost = raise_amount - my_pip

        if (RaiseAction in legal_actions and (raise_cost <= my_stack)):
            temp_action = RaiseAction(raise_amount)

        elif (CallAction in legal_actions and (continue_cost <= my_stack)):
            temp_action = CallAction()

        elif CheckAction in legal_actions:
            temp_action = CheckAction()
        
        else:
            temp_action = FoldAction()

        if board_cards == []:
            key = self.hole_list_to_key(my_cards)
            strength = self.starting_strengths[key]

        else:
            MONTE_CARLO_ITERS = 400
            strength = self.calc_strength(my_cards, MONTE_CARLO_ITERS, board_cards)
        
        if continue_cost > 0:
            scary = 0

            if continue_cost > 6:
                scary = 0.15
            if continue_cost > 12:
                scary = 0.25
            if continue_cost > 50:
                scary = 0.35
            
            strength = max([0, strength - scary])

            pot_odds = continue_cost / (pot_total + continue_cost)

            if strength > pot_odds:
                if random.random() < strength and strength  > 0.5:
                    my_action = temp_action
                else:
                    my_action = CallAction()

            else:
                my_action = FoldAction()

        else:
            if random.random() < strength:
                my_action = temp_action
            
            else:
                my_action = CheckAction()
        self.final_action = my_action
        return my_action
    
    def hole_list_to_key(self, hole):
        '''
        Converts a hole card list into a key that we can use to query our 
        strength dictionary
        hole: list - A list of two card strings in the engine's format (Kd, As, Th, 7d, etc.)
        '''

        card_1 = hole[0] #get all of our relevant info
        card_2 = hole[1]

        rank_1, suit_1 = card_1[0], card_1[1] #card info
        rank_2, suit_2 = card_2[0], card_2[1]

        #to determine color (for abstraction)
        if card_1[1] == 'h' or card_1[1] == 'd':
            card_1_color = 'r'
        
        else:
            card_1_color = 'b'
        
        if card_2[1] == 'h' or card_2[1] == 'd':
            card_2_color = 'r'
        
        else:
            card_2_color = 'b'

        if card_1_color == card_2_color:
            if card_1_color == 'r':
                color_string = 'r'
            else:
                color_string = 'b'
        
        else:
            color_string = 'm'
        
        numeric_1, numeric_2 = self.rank_to_numeric(rank_1), self.rank_to_numeric(rank_2) #make numeric

        suited = suit_1 == suit_2 #off-suit or not
        suit_string = 's' if suited else 'o'

        if numeric_1 >= numeric_2: #keep our hole cards in rank order
                return rank_1 + rank_2 + suit_string + color_string
        else:
            return rank_2 + rank_1 + suit_string + color_string 

    def rank_to_numeric(self, rank):
        '''
        Method that converts our given rank as a string
        into an integer ranking
        rank: str - one of 'A, K, Q, J, T, 9, 8, 7, 6, 5, 4, 3, 2'
        '''
        if rank.isnumeric(): #2-9, we can just use the int version of this string
            return int(rank)
        elif rank == 'T': #10 is T, so we need to specify it here
            return 10
        elif rank == 'J': #Face cards for the rest of them
            return 11
        elif rank == 'Q':
            return 12
        elif rank == 'K':
            return 13
        else: #Ace (A) is the only one left, give it the highest rank
            return 14

    def calc_strength(self, hole, iterations, board_card):
        deck = eval7.Deck()
        hole_card = [eval7.Card(card) for card in hole]
        board_card = [eval7.Card(card) for card in board_card]
        if len(board_card) == 3:
            state = "flop"
        elif len(board_card) == 4:
            state = "turn"
        elif len(board_card) == 5:
            state = "river"
        else:
            state = "run"

        for card in hole_card + board_card:
            deck.cards.remove(card)

        score = 0

        for _ in range(iterations):
            deck.shuffle()

            _COMM = 5 - len(board_card)
            _OPP = 2



            draw = deck.peek(26)
            opp_hole = draw[:_OPP]
            community = board_card + draw[_OPP:_OPP+_COMM]

            for i in range(len(draw)):
                card = draw[_OPP+_COMM+i-1]
                if int(str(card.suit)) not in [1,2]: #1 represents diamond, 2 represents heart
                    break
                community = community + [draw[_OPP  + _COMM + i]]

            our_hand = hole_card + community
            opp_hand = opp_hole + community

            our_value = eval7.evaluate(our_hand)
            opp_value = eval7.evaluate(opp_hand)

            if our_value > opp_value:
                score += 2
            if our_value == opp_value:
                score += 1
            else:
                score += 0
        
        hand_strength = score / (2 * iterations)
        print('the probability of you winning our hand, knowing the', state, 'over', iterations, 'trials is:', hand_strength)

        return hand_strength

if __name__ == '__main__':
    run_bot(Player(), parse_args())
