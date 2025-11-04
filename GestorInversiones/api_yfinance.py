import yfinance as yf

def get_current_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")['Close'].iloc[-1]
        return round(price, 2)
    except Exception as e:
        return 0.0