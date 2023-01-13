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
        # #big_blind = bool(active)  # True if you are the big blind    
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
        
        print(my_cards) #, 'hand =', eval7.evaluate)
        print(opp_cards)
        print(self.board_cards)

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

        if street == 0:
            strength = 1

        else:
            MONTE_CARLO_ITERS = 100
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
        
        return my_action
    

    # def allocate_cards(self, my_cards):
    #     ranks = {} # number:suite

    #     for card in my_cards: #for card in hand
    #         card_rank = card[0]
    #         card_suite = card[1]

    #         if card_rank in ranks:
    #             ranks[card_rank].append(card_suite)
    #         else:
    #             ranks[card_rank] = [card_suite]
        
    #     singles = []
    #     pairs = []

    #     for rank in ranks:
    #         if len(ranks[rank]) == 1:
    #             singles.append(rank)
    #         else:
    #             pairs.append(rank)
        
    #     if len(pairs) > 0:
    #         self.strong_hole = True
    
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

            # while _COMM <= 26:
            #     extra_card = random.randint(0,1)
            #     if extra_card == 0:
            #         break
            #     _COMM += extra_card




            draw = deck.peek(26)
            opp_hole = draw[:_OPP]
            community = board_card + draw[_OPP:_OPP+_COMM]

            for i in range(len(draw)):
                card = draw[_OPP+_COMM+i-1]
                print(card.suit)
                if int(str(card.suit)) not in [1,2]: #1 represents diamond, 2 represents heart
                    break
                community = community + [draw[_OPP  + _COMM + i]]

            for card in draw:
                print(card)
                print(card.rank)
                print(card.suit)

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

    # def find_all_cards(self, my_cards, board_cards, sortby):
    #     all_cards = my_cards + board_cards
    #     if sortby == 'ranks':
    #         ranks = {} # number:suite

    #         for card in all_cards: #for card in hand
    #             card_rank = card[0]
    #             card_suite = card[1]

    #             if card_rank in ranks:
    #                 ranks[card_rank].append(card_suite)
    #             else:
    #                 ranks[card_rank] = [card_suite]
    #         return ranks

    #     elif sortby == 'suites':
    #         suites = {} # suite:number

    #         for card in all_cards: #for card in hand
    #             card_rank = card[0]
    #             card_suite = card[1]

    #             if card_suite in suite:
    #                 ranks[card_suite].append(card_suite)
    #             else:
    #                 ranks[card_suite] = [card_rank]
    #         return suites

if __name__ == '__main__':
    run_bot(Player(), parse_args())