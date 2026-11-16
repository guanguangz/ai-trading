"""A starter file for trying out your own trading rule.

Write your idea inside `my_rule` below, then run:  python my_strategy.py

It reuses the download and scoring code from backtest.py, so this file
only has to contain the rule itself.
"""

import pandas as pd

from backtest import START_DATE, STARTING_CASH, TICKER, download_prices, summarize


def my_rule(close: pd.Series) -> pd.Series:
    """Decide, for every day, whether we want to own the stock.

    `close` is the list of daily closing prices.
    Return True on days you want to own it and False on days you want cash.

    The example rule: own it while the price is above its 200-day average.
    Replace the lines below with your own idea.
    """
    average_200 = close.rolling(200).mean()
    return close > average_200


def main() -> None:
    close = download_prices(TICKER, START_DATE)

    # Turn the rule into 1 (own it) or 0 (cash). We act the day AFTER the
    # rule says so, because we only know today's close once the day is over.
    position = my_rule(close).astype(int).shift(1).fillna(0)

    daily_return = close.pct_change().fillna(0)
    strategy_value = STARTING_CASH * (1 + daily_return * position).cumprod()
    buy_hold_value = STARTING_CASH * (1 + daily_return).cumprod()

    strategy = summarize(strategy_value)
    buy_hold = summarize(buy_hold_value)

    print(f"\n{TICKER} from {close.index[0].date()} to {close.index[-1].date()}, starting with ${STARTING_CASH:,}\n")
    print(f"{'':<18}{'My rule':>14}{'Buy and hold':>14}")
    for name in strategy:
        print(f"{name:<18}{strategy[name]:>14}{buy_hold[name]:>14}")
    print(f"\nMy rule held {TICKER} on {position.mean():.0%} of days.")


if __name__ == "__main__":
    main()
