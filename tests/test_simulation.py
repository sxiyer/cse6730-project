"""
Comprehensive unit tests for the CSE6730 RPS market simulation.
"""
from uuid import UUID

import pytest

from cse6730_project.agents import Agent, Player, PlayerOneCard, Scalper, NaiveGambler, Shadow
from cse6730_project.config import RNG_SEED
from cse6730_project.games import GameOneCard, GameResultType
from cse6730_project.market.markets import MarketCommon
from cse6730_project.models import AgentType, Card, CardPrices, Order, OrderType, Transaction
from cse6730_project.ode.ode import OdeRPS
from cse6730_project.simulation import Simulation
from cse6730_project.utils import logger


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def basicSimulation() -> Simulation:
    return Simulation(market=None, num_players=100, num_scalpers=10, seed=RNG_SEED, num_ticks=2)


@pytest.fixture
def basicODERPS(basicSimulation: Simulation) -> OdeRPS:
    return OdeRPS(
        t_interval=(0, 100),
        t_eval=[0, 100, 10],
        initial_counts=basicSimulation._get_card_counts(agent_type=AgentType.PLAYER),
    )


@pytest.fixture
def market() -> MarketCommon:
    return MarketCommon()


@pytest.fixture
def shadow() -> Shadow:
    return Shadow(uid=UUID(int=0), money=10.0)


@pytest.fixture
def naive_gambler() -> NaiveGambler:
    return NaiveGambler(uid=UUID(int=1), money=10.0)


# ── Models ────────────────────────────────────────────────────────────────────

class TestCardPrices:
    def test_getitem_all_cards(self):
        prices = CardPrices(ROCK=1.0, PAPER=2.0, SCISSOR=3.0)
        assert prices[Card.ROCK] == 1.0
        assert prices[Card.PAPER] == 2.0
        assert prices[Card.SCISSOR] == 3.0

    def test_getitem_invalid_raises(self):
        prices = CardPrices(ROCK=1.0, PAPER=1.0, SCISSOR=1.0)
        with pytest.raises(KeyError):
            _ = prices["invalid"]


class TestOrder:
    def test_default_quantity_is_one(self):
        order = Order(
            agent_UID=UUID(int=0), order_type=OrderType.BUY,
            card_type=Card.ROCK, limit_price=1.0,
        )
        assert order.quantity == 1

    def test_custom_quantity(self):
        order = Order(
            agent_UID=UUID(int=0), order_type=OrderType.SELL,
            card_type=Card.PAPER, limit_price=1.5, quantity=3,
        )
        assert order.quantity == 3

    def test_fields_stored_correctly(self):
        uid = UUID(int=7)
        order = Order(agent_UID=uid, order_type=OrderType.BUY,
                      card_type=Card.SCISSOR, limit_price=0.75)
        assert order.agent_UID == uid
        assert order.order_type == OrderType.BUY
        assert order.card_type == Card.SCISSOR
        assert order.limit_price == 0.75


class TestTransaction:
    def test_fields(self):
        tx = Transaction(agent_UID=UUID(int=5), successful=True)
        assert tx.agent_UID == UUID(int=5)
        assert tx.successful is True

    def test_unsuccessful_transaction(self):
        tx = Transaction(agent_UID=UUID(int=0), successful=False)
        assert tx.successful is False


# ── Players ───────────────────────────────────────────────────────────────────

class TestPlayer:
    def test_initial_deck_all_zero(self):
        p = Player(uid=UUID(int=0))
        assert all(count == 0 for count in p.deck.values())

    def test_initial_money_set_correctly(self):
        p = Player(uid=UUID(int=0), money=15.0)
        assert p.money == 15.0

    def test_uid_set(self):
        uid = UUID(int=42)
        p = Player(uid=uid)
        assert p.UID == uid

    def test_buy_order_returns_none(self):
        p = Player(uid=UUID(int=0))
        prices = CardPrices(ROCK=1.0, PAPER=1.0, SCISSOR=1.0)
        assert p.buy_order(prices) is None

    def test_sell_order_returns_none(self):
        p = Player(uid=UUID(int=0))
        prices = CardPrices(ROCK=1.0, PAPER=1.0, SCISSOR=1.0)
        assert p.sell_order(prices) is None

    def test_shuffle_deck_correct_count(self):
        p = Player(uid=UUID(int=0))
        p.deck[Card.ROCK] = 3
        p.deck[Card.PAPER] = 2
        shuffled = p.shuffleDeck()
        assert len(shuffled) == 5

    def test_shuffle_deck_preserves_card_types(self):
        p = Player(uid=UUID(int=0))
        p.deck[Card.ROCK] = 3
        p.deck[Card.PAPER] = 2
        shuffled = p.shuffleDeck()
        assert shuffled.count(Card.ROCK) == 3
        assert shuffled.count(Card.PAPER) == 2
        assert shuffled.count(Card.SCISSOR) == 0

    def test_shuffle_empty_deck_returns_empty(self):
        p = Player(uid=UUID(int=0))
        assert p.shuffleDeck() == []

    def test_history_starts_empty(self):
        p = Player(uid=UUID(int=0))
        assert p.history == []


class TestPlayerOneCard:
    def test_starts_with_exactly_one_card(self):
        p = PlayerOneCard(uid=UUID(int=0))
        assert sum(p.deck.values()) == 1

    def test_held_card_is_valid_type(self):
        p = PlayerOneCard(uid=UUID(int=0))
        held = [card for card, count in p.deck.items() if count > 0]
        assert len(held) == 1
        assert held[0] in list(Card)


# ── NaiveGambler ──────────────────────────────────────────────────────────────

class TestNaiveGambler:
    def test_buy_order_always_returns_order(self, naive_gambler):
        prices = CardPrices(ROCK=1.0, PAPER=1.0, SCISSOR=1.0)
        assert naive_gambler.buy_order(prices) is not None

    def test_buy_order_type_is_buy(self, naive_gambler):
        prices = CardPrices(ROCK=1.0, PAPER=1.0, SCISSOR=1.0)
        order = naive_gambler.buy_order(prices)
        assert order.order_type == OrderType.BUY

    def test_buy_order_card_is_valid(self, naive_gambler):
        prices = CardPrices(ROCK=1.0, PAPER=1.0, SCISSOR=1.0)
        order = naive_gambler.buy_order(prices)
        assert order.card_type in list(Card)

    def test_buy_order_price_in_range(self, naive_gambler):
        prices = CardPrices(ROCK=1.0, PAPER=1.0, SCISSOR=1.0)
        for _ in range(20):
            order = naive_gambler.buy_order(prices)
            assert 0.5 <= order.limit_price <= 2.0

    def test_buy_order_agent_uid_matches(self, naive_gambler):
        prices = CardPrices(ROCK=1.0, PAPER=1.0, SCISSOR=1.0)
        order = naive_gambler.buy_order(prices)
        assert order.agent_UID == naive_gambler.UID

    def test_sell_order_none_when_empty_deck(self, naive_gambler):
        prices = CardPrices(ROCK=1.0, PAPER=1.0, SCISSOR=1.0)
        assert naive_gambler.sell_order(prices) is None

    def test_sell_order_returns_order_when_holding(self, naive_gambler):
        naive_gambler.deck[Card.ROCK] = 2
        prices = CardPrices(ROCK=1.0, PAPER=1.0, SCISSOR=1.0)
        order = naive_gambler.sell_order(prices)
        assert order is not None
        assert order.order_type == OrderType.SELL

    def test_sell_order_only_sells_owned_card(self, naive_gambler):
        # Only PAPER is owned, so every sell must be PAPER
        naive_gambler.deck[Card.PAPER] = 1
        prices = CardPrices(ROCK=1.0, PAPER=1.0, SCISSOR=1.0)
        for _ in range(20):
            order = naive_gambler.sell_order(prices)
            assert order.card_type == Card.PAPER

    def test_sell_order_price_in_range(self, naive_gambler):
        naive_gambler.deck[Card.ROCK] = 5
        prices = CardPrices(ROCK=1.0, PAPER=1.0, SCISSOR=1.0)
        for _ in range(10):
            order = naive_gambler.sell_order(prices)
            assert 0.5 <= order.limit_price <= 2.0


# ── Shadow ────────────────────────────────────────────────────────────────────

class TestShadowState:
    def test_initial_ema_empty(self, shadow):
        assert shadow._ema == {}

    def test_initial_ema_history_empty(self, shadow):
        assert all(shadow._ema_history[card] == [] for card in Card)

    def test_initial_positions_empty(self, shadow):
        assert shadow._positions == []

    def test_initial_tick_zero(self, shadow):
        assert shadow._current_tick == 0


class TestShadowEMA:
    def test_first_ema_seeds_to_price(self, shadow):
        shadow._update_ema(Card.ROCK, 1.5)
        assert shadow._ema[Card.ROCK] == 1.5
        assert shadow._ema_history[Card.ROCK] == [1.5]

    def test_ema_formula_applied_on_second_call(self, shadow):
        shadow._update_ema(Card.ROCK, 1.0)
        shadow._update_ema(Card.ROCK, 2.0)
        expected = 0.3 * 2.0 + 0.7 * 1.0  # 1.3
        assert shadow._ema[Card.ROCK] == pytest.approx(expected)

    def test_ema_history_accumulates(self, shadow):
        for price in [1.0, 1.2, 1.4]:
            shadow._update_ema(Card.ROCK, price)
        assert len(shadow._ema_history[Card.ROCK]) == 3

    def test_ema_trend_insufficient_history_returns_zero(self, shadow):
        # trend_window=3 requires at least 4 entries
        shadow._ema_history[Card.ROCK] = [1.0, 1.1, 1.2]
        assert shadow._ema_trend(Card.ROCK) == 0.0

    def test_ema_trend_flat_returns_zero(self, shadow):
        shadow._ema_history[Card.ROCK] = [1.5, 1.5, 1.5, 1.5]
        assert shadow._ema_trend(Card.ROCK) == pytest.approx(0.0)


class TestShadowBuyOrder:
    def _seed_uptrend(self, shadow, ema_val=2.0):
        """Pre-seed all cards with uptrend history and EMA=ema_val."""
        for card in Card:
            shadow._ema[card] = ema_val
            shadow._ema_history[card] = [1.5, 1.7, 1.9, ema_val]

    def test_no_buy_when_all_prices_at_ema(self, shadow):
        # First call seeds EMA = price, so ratio = 1.0 exactly → no buy
        prices = CardPrices(ROCK=1.0, PAPER=1.0, SCISSOR=1.0)
        assert shadow.buy_order(prices) is None

    def test_buys_most_underpriced_card(self, shadow):
        self._seed_uptrend(shadow)
        # ROCK is more underpriced than PAPER/SCISSOR
        prices = CardPrices(ROCK=1.9, PAPER=1.98, SCISSOR=1.98)
        order = shadow.buy_order(prices)
        assert order is not None
        assert order.card_type == Card.ROCK
        assert order.order_type == OrderType.BUY

    def test_buy_limit_price_equals_current_price(self, shadow):
        self._seed_uptrend(shadow)
        prices = CardPrices(ROCK=1.9, PAPER=1.98, SCISSOR=1.98)
        order = shadow.buy_order(prices)
        assert order.limit_price == 1.9

    def test_does_not_buy_in_downtrend(self, shadow):
        for card in Card:
            shadow._ema[card] = 2.0
            # Falling history → after update_ema with 1.5, trend stays negative
            shadow._ema_history[card] = [2.5, 2.3, 2.1, 2.0]
        prices = CardPrices(ROCK=1.5, PAPER=1.5, SCISSOR=1.5)
        assert shadow.buy_order(prices) is None

    def test_does_not_double_buy_held_card(self, shadow):
        self._seed_uptrend(shadow)
        # Occupy all three cards in positions
        for card in Card:
            shadow._positions.append((card, 0, 1.5))
        prices = CardPrices(ROCK=1.9, PAPER=1.9, SCISSOR=1.9)
        assert shadow.buy_order(prices) is None

    def test_tick_incremented_each_call(self, shadow):
        prices = CardPrices(ROCK=1.0, PAPER=1.0, SCISSOR=1.0)
        shadow.buy_order(prices)
        shadow.buy_order(prices)
        assert shadow._current_tick == 2


class TestShadowSellOrder:
    def test_no_sell_when_no_positions(self, shadow):
        prices = CardPrices(ROCK=1.0, PAPER=1.0, SCISSOR=1.0)
        assert shadow.sell_order(prices) is None

    def test_trend_reversal_exit(self, shadow):
        shadow.deck[Card.ROCK] = 1
        shadow._positions.append((Card.ROCK, 0, 1.0))
        shadow._current_tick = 5
        shadow._ema[Card.ROCK] = 1.2
        shadow._ema_history[Card.ROCK] = [1.5, 1.4, 1.3, 1.2]  # downtrend
        prices = CardPrices(ROCK=1.1, PAPER=1.0, SCISSOR=1.0)
        order = shadow.sell_order(prices)
        assert order is not None
        assert order.card_type == Card.ROCK
        assert order.order_type == OrderType.SELL
        assert len(shadow._positions) == 0

    def test_recovery_exit_when_price_reaches_ema(self, shadow):
        shadow.deck[Card.ROCK] = 1
        shadow._positions.append((Card.ROCK, 0, 0.9))
        shadow._current_tick = 3
        shadow._ema[Card.ROCK] = 1.0
        shadow._ema_history[Card.ROCK] = [1.0, 1.0, 1.0, 1.0]  # flat → trend = 0
        prices = CardPrices(ROCK=1.0, PAPER=0.9, SCISSOR=0.9)
        order = shadow.sell_order(prices)
        assert order is not None
        assert order.card_type == Card.ROCK
        assert order.order_type == OrderType.SELL

    def test_forced_exit_after_max_hold_ticks(self, shadow):
        shadow.deck[Card.ROCK] = 1
        shadow._current_tick = 15  # 15 - 0 = 15 >= max_hold_ticks(12)
        shadow._positions.append((Card.ROCK, 0, 1.0))
        shadow._ema[Card.ROCK] = 1.5
        shadow._ema_history[Card.ROCK] = [1.5, 1.5, 1.5, 1.5]  # flat, no trend exit
        prices = CardPrices(ROCK=1.2, PAPER=1.0, SCISSOR=1.0)  # below EMA, no recovery
        order = shadow.sell_order(prices)
        assert order is not None
        assert order.card_type == Card.ROCK

    def test_no_forced_exit_before_max_hold_ticks(self, shadow):
        shadow.deck[Card.ROCK] = 1
        shadow._current_tick = 5  # 5 - 0 = 5 < 12
        shadow._positions.append((Card.ROCK, 0, 1.0))
        shadow._ema[Card.ROCK] = 1.5
        shadow._ema_history[Card.ROCK] = [1.5, 1.5, 1.5, 1.5]
        prices = CardPrices(ROCK=1.2, PAPER=1.0, SCISSOR=1.0)
        assert shadow.sell_order(prices) is None

    def test_position_removed_on_sell(self, shadow):
        shadow.deck[Card.ROCK] = 1
        shadow._positions.append((Card.ROCK, 0, 1.0))
        shadow._ema[Card.ROCK] = 1.0
        shadow._ema_history[Card.ROCK] = [1.0, 1.0, 1.0, 1.0]
        prices = CardPrices(ROCK=1.0, PAPER=1.0, SCISSOR=1.0)  # recovery exit
        shadow.sell_order(prices)
        assert len(shadow._positions) == 0

    def test_skips_position_when_deck_empty(self, shadow):
        # Position recorded but deck count is 0 (already sold or never bought)
        shadow.deck[Card.ROCK] = 0
        shadow._positions.append((Card.ROCK, 0, 1.0))
        prices = CardPrices(ROCK=1.0, PAPER=1.0, SCISSOR=1.0)
        assert shadow.sell_order(prices) is None


class TestShadowWakeUpAgent:
    def _seed_buy_signal(self, shadow):
        """Force a buy signal on ROCK."""
        for card in Card:
            shadow._ema[card] = 2.0
            shadow._ema_history[card] = [1.5, 1.7, 1.9, 2.0]

    def test_records_post_clearing_price_in_position(self, shadow):
        self._seed_buy_signal(shadow)
        prices = CardPrices(ROCK=1.9, PAPER=1.98, SCISSOR=1.98)
        buy_order, _, callback = shadow.wake_up_agent(prices)
        assert buy_order is not None

        post_price = 2.1  # price moved after clearing
        callback(successful=True, exchanged_prices={Card.ROCK: post_price, Card.PAPER: 1.98, Card.SCISSOR: 1.98})
        assert len(shadow._positions) == 1
        assert shadow._positions[0][2] == post_price

    def test_buy_updates_deck_and_deducts_money(self, shadow):
        self._seed_buy_signal(shadow)
        prices = CardPrices(ROCK=1.9, PAPER=1.98, SCISSOR=1.98)
        buy_order, _, callback = shadow.wake_up_agent(prices)
        assert buy_order is not None
        initial_money = shadow.money
        callback(
            successful=True,
            exchanged_prices={Card.ROCK: 1.9, Card.PAPER: 1.98, Card.SCISSOR: 1.98},
        )
        assert shadow.deck[buy_order.card_type] == 1
        assert shadow.money == pytest.approx(initial_money - 1.9)

    def test_failed_transaction_does_not_update_state(self, shadow):
        self._seed_buy_signal(shadow)
        prices = CardPrices(ROCK=1.9, PAPER=1.98, SCISSOR=1.98)
        buy_order, _, callback = shadow.wake_up_agent(prices)
        initial_money = shadow.money
        callback(successful=False, exchanged_prices={Card.ROCK: 1.9, Card.PAPER: 1.98, Card.SCISSOR: 1.98})
        assert shadow.money == initial_money
        assert len(shadow._positions) == 0

    def test_sell_callback_increments_money_and_decrements_deck(self, shadow):
        shadow.deck[Card.ROCK] = 1
        shadow._positions.append((Card.ROCK, 0, 0.9))
        shadow._current_tick = 3
        shadow._ema[Card.ROCK] = 1.0
        shadow._ema_history[Card.ROCK] = [1.0, 1.0, 1.0, 1.0]
        prices = CardPrices(ROCK=1.0, PAPER=0.5, SCISSOR=0.5)
        _, sell_order, callback = shadow.wake_up_agent(prices)
        assert sell_order is not None
        initial_money = shadow.money
        callback(successful=True, exchanged_prices={Card.ROCK: 1.0, Card.PAPER: 0.5, Card.SCISSOR: 0.5})
        assert shadow.money == pytest.approx(initial_money + 1.0)
        assert shadow.deck[Card.ROCK] == 0


# ── MarketCommon ──────────────────────────────────────────────────────────────

class TestMarketCommon:
    def test_initial_prices_all_one(self, market):
        prices = market.get_prices()
        for card in Card:
            assert prices[card] == 1.0

    def test_initial_stock_all_thousand(self, market):
        for card in Card:
            assert market.stock[card] == 1000

    def test_get_prices_returns_card_prices_object(self, market):
        assert isinstance(market.get_prices(), CardPrices)

    def test_buy_rejected_when_price_too_low(self, market):
        market.buy_list = []
        order = Order(agent_UID=UUID(int=0), order_type=OrderType.BUY,
                      card_type=Card.ROCK, limit_price=0.50)
        assert market.submit_order(order) is False

    def test_buy_accepted_at_exact_market_price(self, market):
        market.buy_list = []
        order = Order(agent_UID=UUID(int=0), order_type=OrderType.BUY,
                      card_type=Card.ROCK, limit_price=1.0)
        assert market.submit_order(order) is True

    def test_buy_accepted_above_market_price(self, market):
        market.buy_list = []
        order = Order(agent_UID=UUID(int=0), order_type=OrderType.BUY,
                      card_type=Card.ROCK, limit_price=1.5)
        assert market.submit_order(order) is True

    def test_buy_rejected_when_no_stock(self, market):
        market.buy_list = []
        market.stock[Card.ROCK] = 0
        order = Order(agent_UID=UUID(int=0), order_type=OrderType.BUY,
                      card_type=Card.ROCK, limit_price=1.0)
        assert market.submit_order(order) is False

    def test_sell_always_accepted(self, market):
        market.sell_list = []
        order = Order(agent_UID=UUID(int=0), order_type=OrderType.SELL,
                      card_type=Card.ROCK, limit_price=0.01)
        assert market.submit_order(order) is True

    def test_clear_buy_deducts_stock(self, market):
        market.buy_list = [Order(agent_UID=UUID(int=0), order_type=OrderType.BUY,
                                 card_type=Card.ROCK, limit_price=1.0)]
        market.sell_list = []
        market.clear()
        assert market.stock[Card.ROCK] == 999

    def test_clear_sell_adds_stock(self, market):
        market.buy_list = []
        market.sell_list = [Order(agent_UID=UUID(int=0), order_type=OrderType.SELL,
                                  card_type=Card.ROCK, limit_price=1.0)]
        market.clear()
        assert market.stock[Card.ROCK] == 1001

    def test_clear_price_rises_five_percent_on_net_buy(self, market):
        market.buy_list = [Order(agent_UID=UUID(int=0), order_type=OrderType.BUY,
                                 card_type=Card.ROCK, limit_price=1.0)]
        market.sell_list = []
        market.clear()
        assert market.prices[Card.ROCK] == pytest.approx(1.05)

    def test_clear_price_falls_five_percent_on_net_sell(self, market):
        market.buy_list = []
        market.sell_list = [Order(agent_UID=UUID(int=0), order_type=OrderType.SELL,
                                  card_type=Card.ROCK, limit_price=1.0)]
        market.clear()
        assert market.prices[Card.ROCK] == pytest.approx(0.95)

    def test_clear_price_unchanged_when_balanced(self, market):
        market.buy_list = [Order(agent_UID=UUID(int=0), order_type=OrderType.BUY,
                                 card_type=Card.ROCK, limit_price=1.0)]
        market.sell_list = [Order(agent_UID=UUID(int=1), order_type=OrderType.SELL,
                                  card_type=Card.ROCK, limit_price=1.0)]
        market.clear()
        assert market.prices[Card.ROCK] == pytest.approx(1.0)

    def test_clear_unaffected_cards_keep_price(self, market):
        market.buy_list = [Order(agent_UID=UUID(int=0), order_type=OrderType.BUY,
                                 card_type=Card.ROCK, limit_price=1.0)]
        market.sell_list = []
        market.clear()
        assert market.prices[Card.PAPER] == pytest.approx(1.0)
        assert market.prices[Card.SCISSOR] == pytest.approx(1.0)

    def test_clear_deduplicates_agent_with_both_orders(self, market):
        uid = UUID(int=0)
        market.buy_list = [Order(agent_UID=uid, order_type=OrderType.BUY,
                                 card_type=Card.ROCK, limit_price=1.0)]
        market.sell_list = [Order(agent_UID=uid, order_type=OrderType.SELL,
                                  card_type=Card.PAPER, limit_price=1.0)]
        txns = market.clear()
        assert len(txns) == 1
        assert txns[0].agent_UID == uid

    def test_clear_returns_one_transaction_per_distinct_agent(self, market):
        market.buy_list = [
            Order(agent_UID=UUID(int=0), order_type=OrderType.BUY,
                  card_type=Card.ROCK, limit_price=1.0),
            Order(agent_UID=UUID(int=1), order_type=OrderType.BUY,
                  card_type=Card.PAPER, limit_price=1.0),
        ]
        market.sell_list = []
        txns = market.clear()
        assert len(txns) == 2
        uids = {t.agent_UID for t in txns}
        assert UUID(int=0) in uids
        assert UUID(int=1) in uids

    def test_clear_resets_order_lists(self, market):
        market.buy_list = [Order(agent_UID=UUID(int=0), order_type=OrderType.BUY,
                                 card_type=Card.ROCK, limit_price=1.0)]
        market.sell_list = []
        market.clear()
        assert market.buy_list == []
        assert market.sell_list == []

    def test_insert_orders_sets_buy_and_sell_lists(self, market):
        buy = [Order(agent_UID=UUID(int=0), order_type=OrderType.BUY,
                     card_type=Card.ROCK, limit_price=1.0)]
        sell = [Order(agent_UID=UUID(int=1), order_type=OrderType.SELL,
                      card_type=Card.PAPER, limit_price=1.0)]
        market.insert_orders(buy, sell)
        assert market.buy_list == buy
        assert market.sell_list == sell

    def test_buy_rejected_when_stock_below_quantity(self, market):
        market.buy_list = []
        market.stock[Card.ROCK] = 2
        order = Order(agent_UID=UUID(int=0), order_type=OrderType.BUY,
                      card_type=Card.ROCK, limit_price=1.0, quantity=3)
        assert market.submit_order(order) is False


# ── Games ─────────────────────────────────────────────────────────────────────

class TestGameOneCard:
    def _player_with(self, uid_int: int, card: Card) -> Player:
        p = Player(uid=UUID(int=uid_int))
        p.deck[card] = 1
        return p

    def test_rock_beats_scissor(self):
        p1 = self._player_with(0, Card.ROCK)
        p2 = self._player_with(1, Card.SCISSOR)
        game = GameOneCard(p1, p2, tick=0)
        result = game.play()
        assert result == GameResultType.WIN
        assert game.winner is p1
        assert game.loser is p2

    def test_scissor_beats_paper(self):
        p1 = self._player_with(0, Card.SCISSOR)
        p2 = self._player_with(1, Card.PAPER)
        game = GameOneCard(p1, p2, tick=0)
        result = game.play()
        assert result == GameResultType.WIN
        assert game.winner is p1
        assert game.loser is p2

    def test_paper_beats_rock(self):
        p1 = self._player_with(0, Card.PAPER)
        p2 = self._player_with(1, Card.ROCK)
        game = GameOneCard(p1, p2, tick=0)
        result = game.play()
        assert result == GameResultType.WIN
        assert game.winner is p1
        assert game.loser is p2

    def test_same_card_is_tie(self):
        for card in Card:
            p1 = self._player_with(0, card)
            p2 = self._player_with(1, card)
            game = GameOneCard(p1, p2, tick=0)
            result = game.play()
            assert result == GameResultType.TIE

    def test_win_recorded_in_winner_history(self):
        p1 = self._player_with(0, Card.ROCK)
        p2 = self._player_with(1, Card.SCISSOR)
        GameOneCard(p1, p2, tick=0).play()
        assert GameResultType.WIN in p1.history

    def test_loss_recorded_in_loser_history(self):
        p1 = self._player_with(0, Card.ROCK)
        p2 = self._player_with(1, Card.SCISSOR)
        GameOneCard(p1, p2, tick=0).play()
        assert GameResultType.LOSS in p2.history

    def test_tie_recorded_in_both_histories(self):
        p1 = self._player_with(0, Card.PAPER)
        p2 = self._player_with(1, Card.PAPER)
        GameOneCard(p1, p2, tick=0).play()
        assert GameResultType.TIE in p1.history
        assert GameResultType.TIE in p2.history

    def test_rounds_played_increments(self):
        p1 = self._player_with(0, Card.ROCK)
        p2 = self._player_with(1, Card.PAPER)
        game = GameOneCard(p1, p2, tick=0)
        assert game.rounds_played == 0
        game.play()
        assert game.rounds_played == 1

    def test_player_properties(self):
        p1 = self._player_with(0, Card.ROCK)
        p2 = self._player_with(1, Card.PAPER)
        game = GameOneCard(p1, p2, tick=0)
        assert game.player1 is p1
        assert game.player2 is p2


# ── Simulation ────────────────────────────────────────────────────────────────

class TestSimulation:
    def test_init(self, basicSimulation: Simulation) -> None:
        assert len(basicSimulation.players) == 100
        assert basicSimulation.players[69].UID == UUID(int=69)
        assert len(basicSimulation.scalpers) == 10

    def test_run(self, basicSimulation) -> None:
        basicSimulation.run()
        matchA = basicSimulation.matches[0][0].UID
        matchB = basicSimulation.matches[0][1].UID
        logger.info(f"Match at index 0 [player.UID, player.UID] = [{matchA} , {matchB}]")
        samplePlayer: Player = basicSimulation.players[11]
        logger.info(f"Sample Player: {samplePlayer.UID}")
        logger.info(f"{samplePlayer.UID}'s history: {samplePlayer.history}")

    def test_cardcounts(self, basicSimulation: Simulation) -> None:
        cardcounts_players = basicSimulation._get_card_counts(AgentType.PLAYER)
        logger.debug(f"Cards in posession of players: {cardcounts_players}")
        cardcounts_scalpers = basicSimulation._get_card_counts(AgentType.SCALPER)
        logger.debug(f"Cards in posession of scalpers: {cardcounts_scalpers}")

    def test_init_rejects_odd_player_count(self):
        with pytest.raises(AssertionError):
            Simulation(num_players=3, seed=RNG_SEED)

    def test_init_rejects_fewer_than_two_players(self):
        with pytest.raises(AssertionError):
            Simulation(num_players=0, seed=RNG_SEED)

    def test_current_tick_starts_at_zero(self):
        sim = Simulation(num_players=2, seed=RNG_SEED, num_ticks=5)
        assert sim.current_tick == 0

    def test_next_tick_advances_current_tick(self):
        sim = Simulation(num_players=2, seed=RNG_SEED, num_ticks=5)
        sim.next_tick()
        assert sim.current_tick == 1

    def test_run_advances_to_num_ticks(self):
        sim = Simulation(num_players=2, seed=RNG_SEED, num_ticks=3)
        sim.run()
        assert sim.current_tick == 3

    def test_all_players_matched(self):
        sim = Simulation(num_players=4, seed=RNG_SEED, num_ticks=1)
        sim.matchPlayers()
        matched_uids = {agent.UID for pair in sim.matches for agent in pair}
        assert matched_uids == {p.UID for p in sim.players}

    def test_players_have_game_history_after_run(self):
        sim = Simulation(num_players=4, seed=RNG_SEED, num_ticks=3)
        sim.run()
        for p in sim.players:
            assert len(p.history) > 0

    def test_get_card_counts_player_only(self):
        sim = Simulation(num_players=4, num_scalpers=0, seed=RNG_SEED, num_ticks=1)
        counts_scalpers = sim._get_card_counts(AgentType.SCALPER)
        assert all(v == 0 for v in counts_scalpers.values())

    def test_market_integration_changes_scalper_money(self):
        """With a live market, at least one NaiveGambler's balance should change."""
        m = MarketCommon()
        sim = Simulation(
            market=m,
            num_players=2,
            num_scalpers=2,
            scalper_type={NaiveGambler: 1},
            seed=RNG_SEED,
            num_ticks=10,
        )
        initial = [s.money for s in sim.scalpers]
        sim.run()
        final = [s.money for s in sim.scalpers]
        assert any(f != i for f, i in zip(final, initial))

    def test_shadow_beats_naive_gambler_over_many_ticks(self):
        """Shadow's total assets should be >= NaiveGambler's after sufficient ticks."""
        m = MarketCommon()
        sim = Simulation(
            market=m,
            num_players=4,
            num_scalpers=4,
            scalper_type={NaiveGambler: 2, Shadow: 2},
            seed=RNG_SEED,
            num_ticks=50,
        )
        for s in sim.scalpers:
            s.money = 10.0
        sim.run()

        prices = m.get_prices()
        ng_totals = [
            s.money + sum(s.deck[c] * prices[c] for c in Card)
            for s in sim.scalpers if isinstance(s, NaiveGambler)
        ]
        sh_totals = [
            s.money + sum(s.deck[c] * prices[c] for c in Card)
            for s in sim.scalpers if isinstance(s, Shadow)
        ]
        assert sum(sh_totals) >= sum(ng_totals)


# ── ODE ───────────────────────────────────────────────────────────────────────

class TestODE:
    def test_ode(self, basicSimulation: Simulation, basicODERPS: OdeRPS) -> None:
        odeSol = basicODERPS.SolveODE()
        logger.info(f"Got ODE solution w/ data point count = {len(odeSol.y)}")
        logger.debug(f"{odeSol.y}")

    def test_convert_initial_pop_sums_to_one(self, basicODERPS: OdeRPS):
        basicODERPS.convert_initial_pop_to_float()
        total = basicODERPS.d_rock + basicODERPS.d_paper + basicODERPS.d_scissors
        assert total == pytest.approx(1.0)

    def test_initial_pop_list_has_three_elements(self, basicODERPS: OdeRPS):
        assert len(basicODERPS.initial_pop) == 3

    def test_ode_solution_has_three_species(self, basicODERPS: OdeRPS):
        sol = basicODERPS.SolveODE()
        assert sol.y.shape[0] == 3

    def test_ode_solution_has_correct_time_points(self, basicODERPS: OdeRPS):
        sol = basicODERPS.SolveODE()
        # t_eval=[0, 100, 10] → np.linspace(0, 100, 10) = 10 points
        assert sol.y.shape[1] == 10

    def test_ode_populations_non_negative(self, basicODERPS: OdeRPS):
        sol = basicODERPS.SolveODE()
        assert (sol.y >= -1e-9).all()

    def test_ode_populations_conserved(self, basicODERPS: OdeRPS):
        """Total population (sum of all species) is constant throughout integration."""
        sol = basicODERPS.SolveODE()
        col_sums = sol.y.sum(axis=0)
        for s in col_sums:
            assert s == pytest.approx(1.0, abs=1e-6)

    def test_diff_eqn_sum_to_zero(self, basicODERPS: OdeRPS):
        """d/dt(a+b+c) = 0: the three rates sum to zero at any state."""
        import numpy as np
        y = [0.4, 0.35, 0.25]
        dydt = basicODERPS.diff_eqn_szolnoki(0, y)
        assert sum(dydt) == pytest.approx(0.0, abs=1e-12)
