"""Moving-average crossover backtest for SPY, compared with buy-and-hold.

Strategy:
  - Buy  when the 20-day average price crosses ABOVE the 50-day average.
  - Sell when the 20-day average price crosses BELOW the 50-day average.

Run it with:  python backtest.py
"""

import matplotlib

matplotlib.use("Agg")  # draw charts to a file; works without a screen
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

# ---- Settings you can change -------------------------------------------
TICKER = "SPY"            # what to trade
START_DATE = "2010-01-01"  # first day of price history to download
FAST_DAYS = 20            # the "short" moving average
SLOW_DAYS = 50            # the "long" moving average
STARTING_CASH = 10_000    # dollars we pretend to start with
CHART_FILE = "backtest.png"
# -------------------------------------------------------------------------


def download_prices(ticker: str, start: str) -> pd.Series:
    """Download daily closing prices (adjusted for dividends and splits)."""
    data = yf.download(ticker, start=start, auto_adjust=True, progress=False)
    if data.empty:
        raise SystemExit(f"No price data came back for {ticker}. Check your internet connection.")
    close = data["Close"]
    # Newer yfinance versions return a one-column table instead of a simple list.
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    return close.dropna()


def run_backtest(close: pd.Series) -> pd.DataFrame:
    """Work out, day by day, what each approach would be worth."""
    df = pd.DataFrame({"close": close})
    df["fast_avg"] = close.rolling(FAST_DAYS).mean()
    df["slow_avg"] = close.rolling(SLOW_DAYS).mean()

    # Start on the first day both averages exist, so the comparison is fair.
    df = df.dropna().copy()

    # signal = 1 means "we want to own SPY", 0 means "we want to be in cash".
    df["signal"] = (df["fast_avg"] > df["slow_avg"]).astype(int)

    # We only know today's signal after the market closes, so we act on it
    # the NEXT day. Without this shift the backtest would be "peeking" at
    # the future and look better than it really is.
    df["position"] = df["signal"].shift(1).fillna(0)

    # Daily percentage change of SPY.
    df["daily_return"] = df["close"].pct_change().fillna(0)

    # The strategy earns SPY's return only on days we hold it (cash earns 0).
    df["strategy_return"] = df["daily_return"] * df["position"]

    # Grow the starting cash by each day's return.
    df["buy_hold_value"] = STARTING_CASH * (1 + df["daily_return"]).cumprod()
    df["strategy_value"] = STARTING_CASH * (1 + df["strategy_return"]).cumprod()

    # +1 on days we buy, -1 on days we sell, 0 otherwise.
    df["trade"] = df["position"].diff().fillna(df["position"])
    return df


def summarize(values: pd.Series) -> dict:
    """A few standard numbers that describe how an investment did."""
    years = (values.index[-1] - values.index[0]).days / 365.25
    total_return = values.iloc[-1] / values.iloc[0] - 1
    yearly_return = (1 + total_return) ** (1 / years) - 1
    # Max drawdown: the worst drop from a previous high point.
    max_drawdown = (values / values.cummax() - 1).min()
    return {
        "Final value": f"${values.iloc[-1]:,.0f}",
        "Total return": f"{total_return:.1%}",
        "Return per year": f"{yearly_return:.1%}",
        "Worst drop": f"{max_drawdown:.1%}",
    }


def print_results(df: pd.DataFrame) -> None:
    strategy = summarize(df["strategy_value"])
    buy_hold = summarize(df["buy_hold_value"])
    buys = int((df["trade"] > 0).sum())
    sells = int((df["trade"] < 0).sum())
    days_invested = df["position"].mean()

    print(f"\n{TICKER} from {df.index[0].date()} to {df.index[-1].date()}, starting with ${STARTING_CASH:,}\n")
    print(f"{'':<18}{'MA crossover':>14}{'Buy and hold':>14}")
    for name in strategy:
        print(f"{name:<18}{strategy[name]:>14}{buy_hold[name]:>14}")
    print(f"\nThe strategy bought {buys} times and sold {sells} times.")
    print(f"It held {TICKER} on {days_invested:.0%} of days and sat in cash the rest.")


def plot_results(df: pd.DataFrame) -> None:
    fig, (top, bottom) = plt.subplots(
        2, 1, figsize=(11, 8), sharex=True, gridspec_kw={"height_ratios": [3, 2]}
    )

    # Top chart: what each approach is worth over time.
    top.plot(df.index, df["buy_hold_value"], label="Buy and hold", color="#6b7280", linewidth=1.5)
    top.plot(df.index, df["strategy_value"], label=f"{FAST_DAYS}/{SLOW_DAYS} MA crossover", color="#2563eb", linewidth=1.8)
    top.set_title(f"{TICKER}: moving-average crossover vs. buy and hold (${STARTING_CASH:,} start)")
    top.set_ylabel("Portfolio value")
    top.yaxis.set_major_formatter(lambda x, _: f"${x:,.0f}")
    top.legend(loc="upper left", frameon=False)

    # Bottom chart: the price, the two averages, and where we traded.
    bottom.plot(df.index, df["close"], label="Price", color="#9ca3af", linewidth=1)
    bottom.plot(df.index, df["fast_avg"], label=f"{FAST_DAYS}-day average", color="#2563eb", linewidth=1)
    bottom.plot(df.index, df["slow_avg"], label=f"{SLOW_DAYS}-day average", color="#d97706", linewidth=1)
    buys = df[df["trade"] > 0]
    sells = df[df["trade"] < 0]
    bottom.scatter(buys.index, buys["close"], marker="^", color="#16a34a", s=40, zorder=3, label="Buy")
    bottom.scatter(sells.index, sells["close"], marker="v", color="#dc2626", s=40, zorder=3, label="Sell")
    bottom.set_ylabel(f"{TICKER} price")
    bottom.yaxis.set_major_formatter(lambda x, _: f"${x:,.0f}")
    bottom.legend(loc="upper left", frameon=False, ncol=5, fontsize=9)

    for ax in (top, bottom):
        ax.grid(alpha=0.25)
        ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    fig.savefig(CHART_FILE, dpi=150)
    print(f"\nChart saved to {CHART_FILE}")


def main() -> None:
    close = download_prices(TICKER, START_DATE)
    results = run_backtest(close)
    print_results(results)
    plot_results(results)


if __name__ == "__main__":
    main()
