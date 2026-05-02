| Rock x Paper x Scissors - Agent-Based Market Simulation |
|:----:|
| ![Simulation Output](plots/ode/20260501_212418_01.png) |

# CSE6730 Final Project - Rock, Paper, Scissors, Scalpers

## Group 10

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![uv](https://img.shields.io/badge/package_manager-uv-DE5FE9?style=flat-square)
![GT](https://img.shields.io/badge/Georgia_Tech-CSE6730-B3A369?style=flat-square)

--- 

### Team Members

| Name | Email |
|:-----|:------|
| Denys Chernenko | `dchernenko3@gatech.edu` |
| Smaran Iyer | `siyer358@gatech.edu` |
| Adrian Lozada | `alozada7@gatech.edu` |

--- 

### Project Description

In this project, we implement a **Rock-Paper-Scissors (RPS)** game simulation. The simulation involves multiple agents playing against each other. There are two types of agents: **players** and **scalpers**. Players compete against each other while scalpers act as intermediaries who profit from discrepancies in card values or high-demand card shortages. The _objective_ of **players** is `to win as many games as possible`. **Scalpers** aim to predict future card values and buy/sell them `to make a profit`. Cards can be traded for points (the currency of the game), and both players and scalpers use points to buy and sell cards. The game is played in rounds; the player who wins a round receives one point.

### Game Rules

1. Each player starts with a deck of 9 cards consisting of randomly generated combinations of rock, paper, and scissors. There will be an even number of players.

2. Each round, two players are randomly selected to play against each other.

3. Each player randomly shuffles their deck and selects the top card to play. A card cannot be reused in the same round but can be used in future rounds.

4. The first player to win 3 sub-rounds wins the game. The winner receives one point.

5. After each game, players can use their points to buy new cards from a card market. Card prices fluctuate based on supply and demand.

--- 

### Setup Instructions

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) (fast Python package manager):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install dependencies from the project root (uv creates a virtual environment automatically):

```bash
uv sync
```

3. To add or update packages:

```bash
uv add <package>       # add a dependency
uv remove <package>    # remove a dependency
```

4. Prefix any command with `uv run` to execute it inside the managed environment without manually activating it:

```bash
uv run python -m cse6730_project
```

--- 

### Running the Simulation

```bash
uv run python -m cse6730_project
```

--- 

### Running Tests

Run the full test suite:

```bash
uv run pytest tests/
```

Run each test file individually:

```bash
uv run pytest tests/test_simulation.py
uv run pytest tests/test_error_estimation.py
uv run pytest tests/test_ode_solver_timing.py
uv run pytest tests/test_plots.py
```

Run a single test by name:

```bash
uv run pytest tests/test_simulation.py::TestSimulation::test_init
uv run pytest tests/test_simulation.py::TestSimulation::test_run
uv run pytest tests/test_simulation.py::TestSimulation::test_cardcounts
uv run pytest tests/test_simulation.py::TestSimulation::test_ode
uv run pytest tests/test_simulation.py::TestSimulation::test_market_interactions
uv run pytest tests/test_simulation.py::TestMakert::test_market
uv run pytest tests/test_error_estimation.py::test_normalised_rmse_per_card
uv run pytest tests/test_error_estimation.py::test_normalised_mae_per_card
uv run pytest tests/test_error_estimation.py::test_error_plot
uv run pytest tests/test_error_estimation.py::test_per_card_error_summary
uv run pytest tests/test_ode_solver_timing.py::test_solver_timing_smoke
uv run pytest tests/test_plots.py::test_ode_plot
uv run pytest tests/test_plots.py::test_comparison_plot
```

--- 

### Project Structure

```txt
cse6730-project/
├── figures/
├── plots/
│   └── public/
├── INSTRUCTIONS.md
├── pyproject.toml
├── pyrightconfig.json
├── README.md
├── scripts/
│   ├── genWorkTree.sh
│   └── run.sh
├── src/
│   └── cse6730_project/
│       ├── __init__.py
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── player.py
│       │   ├── player_onecard.py
│       │   └── scalper.py
│       ├── config.py
│       ├── games/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── game_one_card.py
│       ├── main.py
│       ├── market/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── market_common.py
│       │   └── market_simple.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── data_models.py
│       ├── reporting.py
│       ├── simulation/
│       │   ├── __init__.py
│       │   └── simulation.py
│       ├── utils.py
│       └── visualization.py
└── tests/
    ├── test_error_estimation.py
    ├── test_ode_solver_timing.py
    ├── test_plots.py
    ├── test_simulation.py
    └── validation.py
```

--- 

### AI Statement

1. OpenAI ChatGPT was used for finding and aggregating relevant research papers. It was also used for formatting bib references. All papers listed were read and distilled into the literature review by a human.
2. Anthropic Claude was used for generating UML diagrams based on human descriptions and code references.
3. Anthropic Claude was used to generate unit tests by scanning the codebase. All produced code was thoroughly reviewed by a human.
4. Anthropic Claude was used to run the scalper code 20 times and aggregate the results.
5. Anthropic Claude was used for generating plotting/visualization code and error estimation code.
6. Anthropic Claude was used to style and comment code to enable easy comprehension by other teammates.
7. GPT 5.3 was used for LaTeX formatting and language editing.
8. Antropic Claude Wrote this Readme :)
---

<div align="center">
<sub>CSE 6730 · Modeling & Simulation x Georgia Institute of Technology x Spring 2026</sub>
</div>
