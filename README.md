# Synovus - F&E Growth (80/20) Strategy

## Overview

This Streamlit app estimates the changes of a portfolio over a date range given an initial investment and assuming the Q2 2025 allocations of:

```
F&E Growth (80/20) Strategy
Strategy Inception Date: 7/01/1996
Synovus Trust Company, N.A.
Foundation & Endowments
```

## Allocation %

### Equity

Subtotal weight: 78.000%

- SPY - SPDR S&P 500 ETF: 47.850
- JMVYX - JPMorgan Mid Cap Value R6 - 8.803
- VXUS - Vanguard Total International Stock Index ETF - 5.100
- VWILX - Vanguard International Growth Admiral - 4.950
- VTRIX - Vanguard International Value Investor - 4.950
- VCRIX - NYLI CBRE Global Infrastructure I - 3.000
- JDMNX - Janus Henderson Enterprise N - 2.447
- QUAYX - AB Small Cap Growth Advisor - 0.450
- FIKNX - Fidelity Advisor Small Cap Value Z - 0.450

### Fixed Income

Subtotal weight: 14.000%

- BIMIX - Baird Intermediate Bond Inst - 6.300
- GVI - iShares Intermediate Govt/Credit ETF - 6.300
- DODIX - Dodge & Cox Income I - 1.400

### Cash

Subtotal weight: 8.000%

- GOIXX - Federated Hermes Government Obligations IS - 8.000

## Usage

Enter / adjust the following inputs as needed:
- Initial amount ($)
- Start date
- End date

Output summary:
- End value
- Absolute change

Output per component:
- Asset Name
- Allocation %
- Start Price
- End Price
- Shares
- End Value

## Local development

### Virtual environment

```shell
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Start

```shell
streamlit run app.py
```

### Stop

Using macOS:

```
control+c
```

### Deactivate

```shell
deactivate
```
