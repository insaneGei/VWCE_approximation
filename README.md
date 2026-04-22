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
│       └── monthly_run.yml              # GitHub Actions workflow: runs the pipeline monthly
│
├── notebooks/
│   └── VWCE_approximation.ipynb         # Jupyter notebook for exploratory analysis
│
├── portfolio_allocations/               # Downloaded and computed allocation files (auto-updated)
│   ├── SWDA_allocation.xls              # Raw SWDA holdings downloaded from iShares
│   ├── SWDA_allocation.csv              # SWDA holdings converted to CSV
│   ├── XMME_allocation.xlsx             # Raw XMME holdings downloaded from DWS
│   └── VWCE_allocation.xlsx             # VWCE market allocation fetched from Vanguard API
│
├── src/
│   ├── optimization/
│   │   └── optimization_utils.py        # Generic SLSQP optimizer: approximate any target allocation
│   └── vwce/
│       ├── compute_portfolio_allocation.py  # Main entry point: orchestrates the full pipeline
│       ├── download_data.py                 # Downloads latest ETF allocation data from provider websites
│       ├── swda_xls_to_csv.py               # Converts the SWDA .xls file to a clean .csv
│       └── update_spreadsheet.py            # Authenticates with Google Sheets and writes results
│
├── requirements.txt                     # Python dependencies
└── README.md                            # This file
```

### Module descriptions

- **`src/optimization/optimization_utils.py`** — Generic optimizer. `compute_optimal_weights(etf_allocations, target)` takes any DataFrame of ETF country allocations and a target allocation Series, and returns optimal weights via SLSQP. Not tied to any specific ETF.
- **`src/vwce/compute_portfolio_allocation.py`** — Main script for the VWCE use case. Calls all other modules in sequence: downloads fresh data, converts formats, runs the optimization, and updates the Google Sheet.
- **`src/vwce/download_data.py`** — Downloads the latest holdings data for SWDA (iShares), XMME (DWS/Xtrackers) and VWCE (Vanguard GraphQL API) and saves them under `portfolio_allocations/`.
- **`src/vwce/swda_xls_to_csv.py`** — Converts the SWDA `.xls` file (SpreadsheetML XML format, not binary Excel) into a clean CSV suitable for pandas.
- **`src/vwce/update_spreadsheet.py`** — Connects to the Google Sheets API using a service account (credentials stored as a GitHub Secret) and writes the optimal weights, country allocations, and a timestamp.

---

## Automation

I wanted to periodically run this script since the geographical allocation of these funds varies in time. The fluctuation of the geographical allocation is quite likely insignificant and won't affect significantly the portfolio's performance, however, i wanted to compute the best possible approximation at the moment of the month in which i buy my quota of these funds.

The script runs automatically on the **17th of every month at midnight UTC** via GitHub Actions (`.github/workflows/monthly_run.yml`). It can also be triggered manually from the Actions tab using the `workflow_dispatch` event.

After each run, the updated allocation files are committed and pushed back to the repository automatically.

### Required setup

To run this project (locally or via GitHub Actions) you need a Google service account with access to the target Google Sheet.

- **GitHub Actions**: the credentials JSON is stored as a repository secret named `GOOGLE_CREDENTIALS` and injected as an environment variable.
- **Local runs**: place the same JSON at `secrets/google_credentials.json` (the `secrets/` folder is gitignored). The loader in `src/auth/google_credentials.py` prefers `GOOGLE_CREDENTIALS` and falls back to this file.

---

## Portfolio Approximation as a Quadratic Programming Problem

Let $A$ be the $d \times n$ matrix whose columns are the geographical allocation vectors of the $n$ available ETFs, and let $\gamma \in \mathbb{R}^d$ be the target allocation vector (VWCE in the default use case). Here $d$ is the number of countries in the union of all funds.

We want to find weights $w \in \mathbb{R}^n$ that solve:

$$
\min_{w \in \mathbb{R}^n} \| A w - \gamma \|^2 \quad \text{subject to} \quad \sum_i w_i = 1
$$

This is a convex quadratic program. We solve it with `scipy.optimize.minimize` using the SLSQP method, starting from uniform weights $w_i = 1/n$.

The VWCE approximation is a particular instance with $n = 2$ (SWDA and XMME), but `optimization_utils.compute_optimal_weights` works for any number of ETFs and any target.
