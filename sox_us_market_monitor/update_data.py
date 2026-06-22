import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

from constituents import SOX_TICKERS

OUT = Path("data/history.json")
START = "2026-01-01"
ANCHOR_DATE = os.getenv("US_MARKET_CAP_ANCHOR_DATE", "2026-06-18")
ANCHOR_US_CAP = float(os.getenv("US_MARKET_CAP_ANCHOR_USD", "74000000000000"))
BROAD_PROXY = os.getenv("US_MARKET_PROXY", "VTI")

def current_caps():
    result = {}
    for symbol in SOX_TICKERS:
        try:
            t = yf.Ticker(symbol)
            cap = t.fast_info.get("market_cap")
            if not cap:
                cap = t.info.get("marketCap")
            if cap:
                result[symbol] = float(cap)
        except Exception:
            pass
    return result

def prices():
    symbols = SOX_TICKERS + [BROAD_PROXY]
    raw = yf.download(symbols, start=START, auto_adjust=True, progress=False, threads=True)
    if raw.empty:
        raise RuntimeError("No price data returned")
    return raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw[["Close"]]

def main():
    px = prices().dropna(how="all")
    caps = current_caps()
    if len(caps) < 20:
        raise RuntimeError(f"Only {len(caps)} constituent market caps were available")

    # Backcast full company market caps using current market cap and adjusted prices.
    numerator = pd.Series(0.0, index=px.index)
    for symbol, cap in caps.items():
        if symbol not in px.columns:
            continue
        s = px[symbol].dropna()
        if s.empty:
            continue
        numerator = numerator.add(cap * px[symbol] / s.iloc[-1], fill_value=0)

    # Denominator: total U.S.-listed market-cap anchor moved by VTI.
    proxy = px[BROAD_PROXY].dropna()
    anchor_ts = proxy.index[proxy.index <= pd.Timestamp(ANCHOR_DATE)]
    if len(anchor_ts) == 0:
        raise RuntimeError("Anchor date precedes available proxy data")
    anchor_px = proxy.loc[anchor_ts[-1]]
    denominator = ANCHOR_US_CAP * px[BROAD_PROXY] / anchor_px

    df = pd.DataFrame({"numerator": numerator, "denominator": denominator}).dropna()
    df = df[df.index >= pd.Timestamp(START)]
    rows = []
    for dt, r in df.iterrows():
        rows.append({
            "date": dt.strftime("%Y-%m-%d"),
            "sox_market_cap_trn": round(r["numerator"]/1e12, 4),
            "us_market_cap_trn": round(r["denominator"]/1e12, 4),
            "share_pct": round(r["numerator"]/r["denominator"]*100, 4),
        })

    payload = {
        "metric": "SOX 30 constituents full-company market cap / total market cap of all U.S.-listed companies",
        "method": "Estimated daily series. Numerator backcast from current full company market caps and adjusted prices; denominator from a total-market-cap anchor moved by VTI.",
        "anchor_date": ANCHOR_DATE,
        "anchor_us_market_cap_usd": ANCHOR_US_CAP,
        "proxy": BROAD_PROXY,
        "constituents": SOX_TICKERS,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "rows": rows,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated through {rows[-1]['date']} with {len(caps)} constituent caps")

if __name__ == "__main__":
    main()
