# app.py
import datetime as dt
import io

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Synovus - F&E Growth (80/20) Strategy (Q2 2025 Allocation)", layout="centered")
st.title("Synovus - F&E Growth (80/20) Strategy (Q2 2025 Allocation)")

# ---------- Allocation & metadata ----------
ALLOC_PCT = {
    "SPY":   47.850,  # SPDR S&P 500 ETF
    "JMVYX": 8.803,   # JPMorgan Mid Cap Value R6
    "VXUS":  5.100,   # Vanguard Total International Stock Index ETF
    "VWILX": 4.950,   # Vanguard International Growth Admiral
    "VTRIX": 4.950,   # Vanguard International Value Investor
    "VCRIX": 3.000,   # NYLI CBRE Global Infrastructure I
    "JDMNX": 2.447,   # Janus Henderson Enterprise N
    "QUAYX": 0.450,   # AB Small Cap Growth Advisor
    "FIKNX": 0.450,   # Fidelity Advisor Small Cap Value Z
    "BIMIX": 6.300,   # Baird Intermediate Bond Inst
    "GVI":   6.300,   # iShares Intermediate Govt/Credit ETF
    "DODIX": 1.400,   # Dodge & Cox Income I
    "GOIXX": 8.000,   # Federated Hermes Government Obligations IS
}
NAMES = {
    "SPY":   "SPDR® S&P 500® ETF",
    "JMVYX": "JPMorgan Mid Cap Value Fund (R6)",
    "VXUS":  "Vanguard Total International Stock Index ETF",
    "VWILX": "Vanguard International Growth Fund (Admiral)",
    "VTRIX": "Vanguard International Value Fund (Investor)",
    "VCRIX": "NYLI CBRE Global Infrastructure (I)",
    "JDMNX": "Janus Henderson Enterprise Fund (N)",
    "QUAYX": "AB Small Cap Growth Portfolio (Advisor)",
    "FIKNX": "Fidelity Advisor Small Cap Value Fund (Z)",
    "BIMIX": "Baird Intermediate Bond Fund (Institutional)",
    "GVI":   "iShares Intermediate Government/Credit Bond ETF",
    "DODIX": "Dodge & Cox Income Fund (I)",
    "GOIXX": "Federated Hermes Government Obligations (IS)",
}
ALL_TICKERS = list(ALLOC_PCT.keys())

CATEGORY = {
    "SPY": "Equity", "JMVYX": "Equity", "VXUS": "Equity", "VWILX": "Equity",
    "VTRIX": "Equity", "VCRIX": "Equity", "JDMNX": "Equity", "QUAYX": "Equity", "FIKNX": "Equity",
    "BIMIX": "Fixed Income", "GVI": "Fixed Income", "DODIX": "Fixed Income",
    "GOIXX": "Cash",
}

# ---------- Robust price loader ----------
@st.cache_data(show_spinner=False)
def load_prices(tickers, start, end):
    raw = yf.download(
        tickers,
        start=pd.to_datetime(start),
        end=pd.to_datetime(end) + pd.Timedelta(days=1),
        auto_adjust=False,
        progress=False,
        threads=True,
        group_by="column",
    )
    if raw.empty:
        raise RuntimeError("No price data returned. Check tickers or dates.")

    def pick_price_frame(df):
        if isinstance(df.columns, pd.MultiIndex):
            top = df.columns.get_level_values(0)
            if "Adj Close" in top: return df["Adj Close"]
            if "Close" in top: return df["Close"]
            raise KeyError("Neither 'Adj Close' nor 'Close' found in downloaded data.")
        else:
            if "Adj Close" in df.columns:
                out = df[["Adj Close"]]
            elif "Close" in df.columns:
                out = df[["Close"]]
            else:
                raise KeyError("Neither 'Adj Close' nor 'Close' found in downloaded data.")
            # Single ticker case: set column name to ticker
            col_name = tickers if isinstance(tickers, str) else tickers[0]
            out.columns = [col_name]
            return out

    prices = pick_price_frame(raw)

    bad = [c for c in prices.columns if prices[c].isna().all()]
    if bad:
        st.warning(f"No price data for: {', '.join(bad)} — they will be excluded.")
        prices = prices.drop(columns=bad)

    return prices.ffill().bfill()

# ---------- UI ----------
col1, col2, col3 = st.columns(3)
with col1:
    initial = st.number_input("Initial amount ($)", min_value=0.0, value=10_000.00, step=10000.0)
with col2:
    start = st.date_input("Start date", value=dt.date(2025, 8, 8))
with col3:
    end = st.date_input("End date", value=dt.date(2025, 11, 8))

if start > end:
    st.error("Start date must be on or before end date.")
    st.stop()

enabled = st.multiselect(
    "Included tickers (uncheck to exclude)",
    options=ALL_TICKERS,
    default=ALL_TICKERS,
)
if not enabled:
    st.error("Please select at least one ticker.")
    st.stop()

alloc = {k: ALLOC_PCT[k] for k in enabled}
weights_raw = pd.Series(alloc) / 100.0

# ---------- Data ----------
with st.spinner("Loading prices…"):
    prices = load_prices(enabled, start, end)
if prices.empty:
    st.error("No usable price data after filtering.")
    st.stop()

weights = weights_raw.reindex(prices.columns).dropna()
dropped = set(weights_raw.index) - set(weights.index)
if dropped:
    st.warning(f"Dropped due to missing data: {', '.join(sorted(dropped))}")
if weights.empty:
    st.error("All selected tickers lacked price data for the chosen range.")
    st.stop()
weights = weights / weights.sum()

first_prices = prices.iloc[0]
last_prices = prices.iloc[-1]

start_value = float(initial)
shares = (start_value * weights) / first_prices
end_value = float((shares * last_prices).sum())
change_abs = end_value - start_value
change_pct = (end_value / start_value) - 1.0

daily_values = (prices[weights.index] * shares).sum(axis=1).to_frame("Portfolio Value")

# ---------- Output ----------
st.subheader("Results")
st.metric("End value", f"${end_value:,.2f}", delta=f"{change_pct*100:,.2f}%")
st.write(f"Absolute change: ${change_abs:,.2f}")
st.line_chart(daily_values)

# ---------- Component breakdown (categorized + names) ----------
base_breakdown = pd.DataFrame({
    "Name": [NAMES.get(t, t) for t in weights.index],
    "Ticker": weights.index,
    "Category": [CATEGORY.get(t, "Other") for t in weights.index],
    "Weight % (normalized)": (weights * 100).round(3).values,
    "Start Price": first_prices[weights.index].round(4).values,
    "End Price": last_prices[weights.index].round(4).values,
    "Shares": shares[weights.index].round(6).values,
    "End Value": (shares[weights.index] * last_prices[weights.index]).round(2).values,
})

def show_section(title: str, cat: str):
    df = base_breakdown[base_breakdown["Category"] == cat].sort_values(
        by="Weight % (normalized)", ascending=False
    )

    st.markdown(f"#### {title}")
    if df.empty:
        st.caption("No holdings in this section for the current selection/date range.")
        return

    subtotal = df["Weight % (normalized)"].sum()
    st.caption(f"Subtotal weight: **{subtotal:.3f}%**")

    # Reorder so Name is first
    cols = ["Name", "Ticker", "Weight % (normalized)", "Start Price", "End Price", "Shares", "End Value", "Category"]
    df = df[cols]

    st.dataframe(
        df.drop(columns=["Category"]),
        # use_container_width=True,
        width="stretch",
        column_config={
            # Make the Name column roomy; you can also use an explicit int like width=380
            "Name": st.column_config.TextColumn("Name", width="large"),
            # Optional: right-align numeric columns
            "Weight % (normalized)": st.column_config.NumberColumn(format="%.3f"),
            "Start Price": st.column_config.NumberColumn(format="%.4f"),
            "End Price": st.column_config.NumberColumn(format="%.4f"),
            "Shares": st.column_config.NumberColumn(format="%.6f"),
            "End Value": st.column_config.NumberColumn(format="%.2f"),
        },
        hide_index=True,
    )

st.markdown("### Component Detail")
show_section("Equity", "Equity")
show_section("Fixed Income", "Fixed Income")
show_section("Cash", "Cash")

# ---------- Downloads ----------
def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf)
    return buf.getvalue().encode()

st.download_button(
    "Download daily portfolio values (CSV)",
    data=df_to_csv_bytes(daily_values),
    file_name="portfolio_values.csv",
    mime="text/csv",
)

st.download_button(
    "Download full component breakdown (CSV)",
    data=df_to_csv_bytes(
        base_breakdown.sort_values(
            by=["Category", "Weight % (normalized)"], ascending=[True, False]
        )
    ),
    file_name="component_breakdown.csv",
    mime="text/csv",
)

st.caption(
    "Notes: Mutual fund & money-market NAVs post once per day and can appear with a one-day lag. "
    "Weights are renormalized to symbols with valid data for the chosen dates."
)
