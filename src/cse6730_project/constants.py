from cards import Card

RNG_SEED = 69

PLAYER_STARTING_MONEY = 0.0
SCALPER_STARTING_MONEY = 0.0

PAYOFF = {
    (Card.ROCK, Card.SCISSORS) : 1,
    (Card.SCISSORS, Card.PAPER) : 1,
    (Card.PAPER, Card.ROCK) : 1
}