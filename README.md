## Pokerbots Overview:
MIT Pokerbots is a computerized poker tournament, where teams have one month to program a completely autonomous poker bot that competes against other bots in a unique poker variant.
Competitors must learn and apply concepts in mathematics, computer science, and economics not normally developed together in academic settings in order to conquer their opponents and emerge victorious. In the last week, each team’s bots are put against each other in a final tournament, in which our bot placed 22nd out of over 50 teams.

## Current Bot Analysis:
Our bot employs a MonteCarlo approach to estimate hand strengths and determine the pot odd probability to decide what action the bot would take. Every turn, using available hand and board card information, we simulated 1000 matches in which the remaining community cards were randomized and flipped, determining the approximate win probability of our hand assuming both teams made it to the reveal. 

## Optimizations:
One constraint of the MonteCarlo live approach to estimating hand strengths is that it takes a significant time to run, especially as you increase the amount of simulations to perform each turn. This correlates to a slower code and potentially a timed-out bot. We used python pandas to precompute hole card strengths with variant-specific abstractions and stored the data in a csv file which allowed much quicker access during the round. 




## Additional Information

# Abstraction:
The abstraction is a string that takes the suits of the two hole cards and adds two characters afterward representing suited/off-suited & red/black/mixed. For example, pocket aces (diamonds and hearts) would be abstracted as “AAor”. 
In addition to precomputing the hole cards, we precomputed potential board cards post flop per strong (<= .5 hand strength) hole cards. We felt it would be unnecessary to store flop permutations of a weak hole card as a weak hole card is likely to end in a fold. And we also felt it unnecessary to keep all the unique flop combinations of the hole cards evaluated but rather only the hole & flop combinations which resulted in a hand strength of >= .35. In total we ended up evaluating 12,000,000+ hole & flop card combinations after reducing the number of hole cards evaluated and ended up keeping roughly 1,000,000 hole & flop card combinations for constant time access during the game. We felt it unnecessary to precompute any further as once you know the flop the computation necessary to evaluate the hand strength begins to diminish.


