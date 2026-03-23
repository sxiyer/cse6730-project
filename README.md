# CSE6730 Final Project

## Group 10 

### Team Members:

- Denys Chernenko
- Smaran Iyer
- Adrian Lozada

### Project Description:

In this project, we will implement a Rock-Paper-Scissors (RPS) game simulation. The simulation will involve multiple agents playing against each other. There will be two types of agents: players and scalpers. Players will play against each other. The objective of players is to win as much games as possible. Scalpers main goal is to predict the future value of cards and buy and sell them to make a profit. In this simulation, cards can be traded for points (the currency of the game). Players can use their points to buy cards, and scalpers can use their points to buy and sell cards. The game will be played in rounds, and at the end of each round, the player that won will recieve one point. Each player will start with a deck of 9 cards. 

### Game Rules:

1. Each player starts with a deck of 9 cards, consisting of randomly generated combinations of rock, paper, and scissors. There will be a even number of players.

2. Each round, two players are randomly selected to play against each other. 

3. Each player will randomly shuffle their deck and select the top card to play against their opponent. A card can't be reused in the same round, but it can be used in future rounds. 

4. The first player to win 3 rounds wins the game. The winner of each round receives one point.

5. After each game, players can use their points to buy new cards from a card market. The card market will have a limited number of cards available, and the price of each card will fluctuate based on supply and demand.

### Running the Simulation:

1. Need to have *Python 3.12*.

2. Create a virtual environment.

3. Run the following command from the project's root dir to install the required dependencies:

```bash
pip install . 
```
