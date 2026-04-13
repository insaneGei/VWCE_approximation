# VWCE Approximation

## Introduction

The code in this repository serves as a simple tool to periodically compute a portfolio that approximates Vanguard's VWCE ETF using iShares' SWDA ETF and Xtrackers' XMME ETF.

The main reasons behind this exercise are mainly two:

1. Since I recently began earning a salary, I wanted to periodically invest some of it in the VWCE fund. However, my broker charges a small commission when purchasing this title, whilst some other titles (including SWDA and XMME) are free of charge. The commission charged is small, however I took the opportunity to carry out this small project.

2. I am trying to improve some skills about my interests, including programming, data analysis and understanding of the financial markets. Consequently, this small project allowed me to tackle all these topics learning small interesting things (e.g. I had never had to interact with GitHub Actions for cloud batch deployment, nor had I had the need to understand how to connect to Google Cloud's API services).

Moreover, I was happy to solve this problem with an optimization algorithm, which reminds me of my student career as a mathematician!

A small viable development of this project is to add some notebooks with backtest analysis of the obtained portfolio, so as to learn something about financial quantitative analysis and risk analysis applied to something that interests me in first person: my own savings!

---

## File Structure

```
VWCE_approximation/
│
├── .github/
│   └── workflows/
│       └── monthly_run.yml          # GitHub Actions workflow: runs the pipeline monthly
│
├── notebooks/
│   └── SWDA_balancing.ipynb         # Jupyter notebook for exploratory analysis
│
├── portfolio_allocations/           # Downloaded and computed allocation files (auto-updated)
│   ├── SWDA_allocation.xls          # Raw SWDA holdings downloaded from iShares
│   ├── SWDA_allocation.csv          # SWDA holdings converted to CSV
│   ├── XMME_allocation.xlsx         # Raw XMME holdings downloaded from DWS
│   ├── VWCE_allocation.xlsx         # VWCE market allocation fetched from Vanguard API
│   └── VWCE_market_allocation.xlsx  # (legacy) previous version of VWCE allocation
│
├── src/
│   ├── compute_portfolio_allocation.py  # Main entry point: orchestrates the full pipeline
│   ├── download_data.py                 # Downloads latest ETF allocation data from provider websites
│   ├── optimization_utils.py            # Scipy-based optimizer to find optimal SWDA/XMME weights
│   ├── swda_xls_to_csv.py               # Converts the SWDA .xls file to a clean .csv
│   └── update_spreadsheet.py            # Authenticates with Google Sheets and writes results
│
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

### Module descriptions

- **`compute_portfolio_allocation.py`** — Main script. Calls all other modules in sequence: downloads fresh data, converts formats, runs the optimization, and updates the Google Sheet.
- **`download_data.py`** — Downloads the latest holdings data for SWDA (iShares), XMME (DWS/Xtrackers) and VWCE (Vanguard GraphQL API) and saves them under `portfolio_allocations/`.
- **`swda_xls_to_csv.py`** — Converts the SWDA `.xls` file (which has a non-standard format) into a clean CSV suitable for pandas.
- **`optimization_utils.py`** — Implements the SLSQP optimizer that finds the weights $(x, y)$ minimizing the distance between the blended SWDA+XMME portfolio and VWCE.
- **`update_spreadsheet.py`** — Connects to the Google Sheets API using a service account (credentials stored as a GitHub Secret) and writes the optimal weights, country allocations, and a timestamp.

---

## Automation

I wanted to periodically run this script since the geographical allocation of these funds varies in time. The fluctuation of the geographical allocation is quite likely insignificant and won't affect significantly the portfolio's performance, however, i wanted to compute the best possible approximation at the moment of the month in which i buy my quota of these funds.

The script runs automatically on the **17th of every month at midnight UTC** via GitHub Actions (`.github/workflows/monthly_run.yml`). It can also be triggered manually from the Actions tab using the `workflow_dispatch` event.

After each run, the updated allocation files are committed and pushed back to the repository automatically.

### Required setup

To run this project (locally or via GitHub Actions) you need a Google service account with access to the target Google Sheet. The credentials JSON must be stored as a GitHub repository secret named `GOOGLE_CREDENTIALS`.

---

## VWCE Approximation as a Linear Programming Problem

Let $\alpha$, $\beta$ be the vectors of geographical allocation of the SWDA and XMME ETFs respectively, and let $\gamma$ be the allocation vector of the VWCE ETF. We interpret these as $d$-dimensional vectors, where $d$ is the size of the union of all countries covered by the three funds.

We want to minimize the following function:

$$
f\colon \mathbb{R}^2 \to \mathbb{R}
$$

$$
(x, y) \mapsto \|(\alpha, \beta) \cdot (x, y)^\top - \gamma\|^2
$$

which is convex. This is a standard constrained optimization problem, where the weights $(x, y)$ must satisfy the constraint $x + y = 1$ (full investment). We use `scipy.optimize.minimize` with the SLSQP method to solve it.
