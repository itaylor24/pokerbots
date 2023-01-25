'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
import eval7


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
        self.strong_hole = False
        singles = []
        pairs = []
        toak = []
        

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
        #my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        #game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        #round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        # my_cards = round_state.hands[active]  # your cards
        #big_blind = bool(active)  # True if you are the big blind        
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
        #my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        #previous_state = terminal_state.previous_state  # RoundState before payoffs
        #street = previous_state.street  # int of street representing when this round ended
        #my_cards = previous_state.hands[active]  # your cards
        #opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed
        self.strong_hole = False
        pass

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

        self.allocate_cards(my_cards)


        net_upper_raise_bound = round_state.raise_bounds()
        stacks = [my_stack, opp_stack]

        net_cost = 0
        my_action = None

        if (RaiseAction in legal_actions and (self.strong_hole)):
            min_raise, max_raise = round_state.raise_bounds()
            max_cost = max_raise - my_pip

            if max_cost <= my_stack - net_cost:
                my_action = RaiseAction(max_raise)
                net_cost += max_cost

            elif CallAction in legal_actions:
                my_action = CallAction()
                net_cost += continue_cost
            
            else:
                my_action = CheckAction()
        elif CheckAction in legal_actions:
            my_action = CheckAction()

        else:
            my_action = CallAction()
            net_cost += continue_cost

        return my_action



        # if CheckAction in legal_actions:  # check-call
        #     return CheckAction()
        # return CallAction()
    
    def allocate_cards(self, my_cards):
        ranks = {} # number:suite

        for card in my_cards: #for card in hand
            card_rank = card[0]
            card_suite = card[1]

            if card_rank in ranks:
                ranks[card_rank].append(card_suite)
            else:
                ranks[card_rank] = [card_suite]
        
        singles = []
        pairs = []

        for rank in ranks:
            if len(ranks[rank]) == 1:
                singles.append(rank)
            else:
                pairs.append(rank)
        
        if len(pairs) > 0:
            self.strong_hole = True

    def find_all_cards(self, my_cards, board_cards, sortby):
        all_cards = my_cards + board_cards
        if sortby == 'ranks':
            ranks = {} # number:suite

            for card in all_cards: #for card in hand
                card_rank = card[0]
                card_suite = card[1]

                if card_rank in ranks:
                    ranks[card_rank].append(card_suite)
                else:
                    ranks[card_rank] = [card_suite]
            return ranks

        elif sortby == 'suites':
            suites = {} # suite:number

            for card in all_cards: #for card in hand
                card_rank = card[0]
                card_suite = card[1]

                if card_suite in suite:
                    ranks[card_suite].append(card_suite)
                else:
                    ranks[card_suite] = [card_rank]
            return suites

if __name__ == '__main__':
    run_bot(Player(), parse_args())
