import eval7
import itertools
import pandas as pd

def calc_strength(hole, iterations, board_card = []):
    deck = eval7.Deck()
    hole_card = [eval7.Card(card) for card in hole]
    board_card = [eval7.Card(card) for card in board_card]

    for card in hole_card + board_card:
        deck.cards.remove(card)

    score = 0

    for _ in range(iterations):
        deck.shuffle()

        _COMM = 5 - len(board_card)
        _OPP = 2

        draw = deck.peek(28)
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

    return hand_strength

if __name__ == '__main__':
    _MONTE_CARLO_ITERS = 100000
    _RANKS = 'AKQJT98765432'

    off_rank_holes = list(itertools.combinations(_RANKS, 2)) #all holes we can have EXCEPT pocket pairs (e.g. [(A, K), (A, Q), (A, J)...])
    pocket_pair_holes = list(zip(_RANKS, _RANKS)) #all pocket pairs [(A, A), (K, K), (Q, Q)...]

    suited_r_strengths = [calc_strength([hole[0] + 'd', hole[1] + 'd'], _MONTE_CARLO_ITERS) for hole in off_rank_holes] #all holes with the same suit
    suited_b_strengths = [calc_strength([hole[0] + 'c', hole[1] + 'c'], _MONTE_CARLO_ITERS) for hole in off_rank_holes] #all holes with the same suit
    
    off_suit_r_strengths = [calc_strength([hole[0] + 'h', hole[1] + 'd'], _MONTE_CARLO_ITERS) for hole in off_rank_holes] #all holes with off suits
    off_suit_b_strengths = [calc_strength([hole[0] + 'c', hole[1] + 's'], _MONTE_CARLO_ITERS) for hole in off_rank_holes] #all holes with off suits
    off_suit_m_strengths = [calc_strength([hole[0] + 'c', hole[1] + 'd'], _MONTE_CARLO_ITERS) for hole in off_rank_holes] #all holes with off suits

    pocket_pair_r_strengths = [calc_strength([hole[0] + 'h', hole[1] + 'd'], _MONTE_CARLO_ITERS) for hole in pocket_pair_holes] #pocket pairs must be off suit
    pocket_pair_b_strengths = [calc_strength([hole[0] + 'c', hole[1] + 'd'], _MONTE_CARLO_ITERS) for hole in pocket_pair_holes] #pocket pairs must be off suit
    pocket_pair_m_strengths = [calc_strength([hole[0] + 'd', hole[1] + 'c'], _MONTE_CARLO_ITERS) for hole in pocket_pair_holes] #pocket pairs must be off suit


    suited_r_holes = [hole[0] + hole[1] + 'sr' for hole in off_rank_holes] #s == suited
    suited_b_holes = [hole[0] + hole[1] + 'sb' for hole in off_rank_holes] #s == suited

    off_suited_r_holes = [hole[0] + hole[1] + 'or' for hole in off_rank_holes] #o == off-suit
    off_suited_b_holes = [hole[0] + hole[1] + 'ob' for hole in off_rank_holes] #o == off-suit
    off_suited_m_holes = [hole[0] + hole[1] + 'om' for hole in off_rank_holes] #o == off-suit

    pocket_pairs_r = [hole[0] + hole[1] + 'or' for hole in pocket_pair_holes] #pocket pairs are always off suit
    pocket_pairs_b = [hole[0] + hole[1] + 'ob' for hole in pocket_pair_holes] #pocket pairs are always off suit
    pocket_pairs_m = [hole[0] + hole[1] + 'om' for hole in pocket_pair_holes] #pocket pairs are always off suit

    all_strengths = suited_r_strengths + suited_b_strengths + off_suit_r_strengths + off_suit_b_strengths + off_suit_m_strengths + pocket_pair_r_strengths + pocket_pair_b_strengths + pocket_pair_m_strengths #aggregate them all
    all_holes = suited_r_holes + suited_b_holes + off_suited_r_holes + off_suited_b_holes + off_suited_m_holes + pocket_pairs_r + pocket_pairs_b + pocket_pairs_m

    hole_df = pd.DataFrame() #make our spreadsheet with a pandas data frame!
    hole_df['Holes'] = all_holes
    hole_df['Strengths'] = all_strengths

    hole_df.to_csv('new_hole_strengths.csv', index=False) #save it for later use, trade space for time!

