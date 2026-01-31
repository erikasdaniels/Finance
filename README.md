# 📈 UK Personal Finance Portfolio Tools

This repository contains a suite of Python tools designed to model, simulate, and backtest personal finance portfolios, specifically tailored for UK tax wrappers (ISA, LISA, Pension) and property scenarios.

## 🛠 Features

### 1. Portfolio Projector (GUI)
A powerful forward-looking simulation tool with a modern GUI built using `customtkinter`. It allows you to model your net worth growth over decades, factoring in complex UK-specific logic.

**Key Features:**
- **Interactive Sliders**: Real-time adjustment of growth rates, inflation, and ages.
- **UK Tax Wrappers**: Models Pension, Stocks & Shares ISA, Lifetime ISA (LISA), and General Cash.
- **Property Ladder Logic**: Simulates saving for a deposit, buying a house, and mortgage amortization.
- **Retirement Planning**:
  - **Drawdown Waterfall**: Automatically prioritizes withdrawal sources based on age (ISA/Cash first, then Pension > 57, then State Pension > 67).
  - **Gap Funding**: Calculates if you have enough bridging capital to retire early before pension access.
- **Tax Logic**: Estimates take-home pay after Income Tax, National Insurance, and Student Loans (Plan 2/PG).

**File:** `Portfolio_GUI.py`

### 2. Portfolio Backtester
A historical analysis tool that lets you see how a strategy would have performed using real market data.

**Key Features:**
- **Real Market Data**: Fetches historical data via `yfinance` (Yahoo Finance).
- **Indices Supported**: S&P 500, Nasdaq, FTSE 100, Global All-Cap (ACWI).
- **DCA Simulation**: Models an initial lump sum plus monthly Dollar Cost Averaging contributions.
- **Visuals**: Plots total invested vs. current portfolio value over time.

**File:** `Portfolio_Backtester.py`

### 3. CLI Calculator
The original command-line script for quick calculations without a GUI interface.

**File:** `Portfolio Calculator.py`

---

## 🚀 Installation

1. **Clone the repository** (or download the files).
2. **Install dependencies**:
   ```bash
   pip install customtkinter matplotlib yfinance pandas packaging
   ```
   *Note: `tkinter` is usually included with Python, but `customtkinter` adds the modern UI elements.*

---

## 📖 Usage

### Running the Portfolio Projector
```bash
python Portfolio_GUI.py
```
- **Left Panel**: Adjust your salary, current savings, expected returns, and retirement goals.
- **Right Panel**: View the interactive chart showing the growth of each asset class and your total net worth.
- **Retirement**: Set your `Retirement Age` and `Retirement Income`. The model will stop contributions at retirement and start drawing down assets to meet your income needs.

### Running the Backtester
```bash
python Portfolio_Backtester.py
```
- Select an index (e.g., S&P 500).
- Set your historic timeframe (e.g., 10 years).
- Input your starting capital and monthly contribution.
- Click **Run Backtest** to see how your money would have grown.

---

## 🧠 Logic & Assumptions

- **Inflation**: All results can be adjusted for inflation (Real vs. Nominal terms) using the inflation slider.
- **Fiscal Rules**:
  - **Pension Access Age**: 57
  - **LISA Access Age**: 60 (for retirement withdrawals)
  - **State Pension Age**: 67
  - **State Pension Amount**: ~£12,000/year (Auto-adjusted in logic)
- **Growth**: Assumes linear compound growth for the projection (not sequence of returns risk).
- **Mortgage**: Standard repayment mortgage logic included.

## ⚠️ Disclaimer
These tools are for educational and illustrative purposes only. They are **not** financial advice. Tax rules (ISA limits, Pension LTA/Lump sums) change frequently. Always do your own research.
