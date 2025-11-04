# indicadores.py
import os
import requests
import pandas as pd

# ---------- CONFIG CACHE ----------
CACHE_FILE = "indicadores_cache.csv"

def load_cache():
    if os.path.exists(CACHE_FILE):
        return pd.read_csv(CACHE_FILE, index_col="ticker")
    else:
        return pd.DataFrame()

def save_cache(ticker, data):
    df_cache = load_cache()
    new_data = pd.DataFrame([data], index=[ticker])
    df_cache.update(new_data)
    df_cache = pd.concat([df_cache, new_data[~new_data.index.isin(df_cache.index)]])
    df_cache.to_csv(CACHE_FILE)

# ---------- API FMP ----------
def get_fmp_indicators(ticker, fmp_key):
    base_url = "https://financialmodelingprep.com/api/v3"
    result = {}

    try:
        ratios_url = f"{base_url}/ratios-ttm/{ticker}?apikey={fmp_key}"
        r = requests.get(ratios_url)
        data = r.json()
        if data:
            result["Net Profit Margin"] = data[0].get("netProfitMarginTTM", "N/D")
            result["ROIC"] = data[0].get("returnOnInvestedCapitalTTM", "N/D")
            result["Quick Ratio"] = data[0].get("quickRatioTTM", "N/D")
            result["Debt to Equity"] = data[0].get("debtEquityRatioTTM", "N/D")

        dividends_url = f"{base_url}/key-metrics-ttm/{ticker}?apikey={fmp_key}"
        r = requests.get(dividends_url)
        data = r.json()
        if data:
            result["Payout Ratio"] = data[0].get("payoutRatioTTM", "N/D")
    except:
        pass

    return result

# ---------- API Alpha Vantage ----------
def get_alpha_indicators(ticker, alpha_key):
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={alpha_key}"
    result = {}
    try:
        r = requests.get(url)
        data = r.json()
        if "Symbol" in data:
            result["P/E Ratio"] = data.get("PERatio", "N/D")
            result["P/B Ratio"] = data.get("PriceToBookRatio", "N/D")
            result["Dividend Yield"] = data.get("DividendYield", "N/D")
    except:
        pass
    return result

# ---------- Función combinada con caché ----------
def get_all_indicators_with_cache(ticker, alpha_key, fmp_key):
    ticker = ticker.upper()
    cache = load_cache()

    if ticker in cache.index:
        return cache.loc[ticker].to_dict()

    data = {
        "Net Profit Margin": "N/D",
        "ROIC": "N/D",
        "P/E Ratio": "N/D",
        "P/B Ratio": "N/D",
        "Quick Ratio": "N/D",
        "Debt to Equity": "N/D",
        "Dividend Yield": "N/D",
        "Payout Ratio": "N/D"
    }

    data.update(get_fmp_indicators(ticker, fmp_key))
    data.update(get_alpha_indicators(ticker, alpha_key))

    save_cache(ticker, data)
    return data
