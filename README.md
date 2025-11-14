# Synovus - F&E Growth (80/20) Strategy

## Overview

This Streamlit app estimates the changes of a portfolio over a date range given an initial investment and using the asset allocations of:

```
F&E Growth (80/20) Strategy
Strategy Inception Date: 7/01/1996
Synovus Trust Company, N.A.
Foundation & Endowments
```

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
streamlit run streamlit_app.py
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
