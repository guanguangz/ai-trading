# ai-trading

A beginner project for testing trading ideas on past price data ("backtesting").
No real money is involved.

## What it does

`backtest.py` tests a **moving-average crossover** strategy on SPY (a fund that
tracks the S&P 500):

- **Buy** when the 20-day average price crosses above the 50-day average.
- **Sell** when it crosses back below, and wait in cash.

It then compares the result with simply buying SPY on day one and holding it.

## How to run it

You need Python 3.10 or newer and an internet connection (prices are downloaded
from Yahoo Finance).

```bash
pip install -r requirements.txt
```

```bash
python backtest.py
```

This prints a results table and saves a chart to `backtest.png`:

- **Top chart:** the value of $10,000 over time for each approach.
- **Bottom chart:** the SPY price, both averages, and each buy (green) and sell (red).

## Changing the settings

The settings are at the top of `backtest.py`: the ticker, start date, the two
average lengths, and the starting cash. Edit them and run it again.

## What the backtest leaves out

- Trading fees, taxes, and interest earned on cash are ignored.
- Trades happen at the closing price on the day after a crossover.
- Past results do not predict future results. This is for learning, not
  financial advice.
