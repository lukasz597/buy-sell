import yfinance as yf
import pandas as pd
from datetime import datetime

TICKER = "CNDX.AS"


def get_data():
    data = yf.download(
        TICKER,
        period="2y",
        interval="1d",
        auto_adjust=False,
        progress=False
    )

    # zabezpieczenie MultiIndex (czasem yfinance to robi)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)

    return data


def add_sma(data):
    data = data.copy()

    # 🔥 tylko zamknięcia
    close = data["Close"]

    data["SMA20"] = close.rolling(20).mean()
    data["SMA200"] = close.rolling(200).mean()
    # print("LAST DATE:", data.index[-1])
    # print("LAST CLOSE:", data["Close"].iloc[-1])

    return data


def generate_signal(close, sma20, sma200):
    
    if close < sma20 and close < sma200:
        return "BUY"
    elif close > sma20 and close > sma200:
        return "SELL"
    else:
        return "BUY/SELL"
    

def save_html(date, close, sma20, sma200, signal):
    html = f"""
    <html>
    <head>
        <title>CNDX Signal</title>
        <style>
            body {{ font-family: Arial; margin: 20px; }}
            # .box {{ padding: 20px; border: 1px solid #ccc; width: 450px; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>CNDX (IE00B53SZB19)</h2>

            <p><b>Last CLOSED session:</b> {date}</p>
            <p><b>Close:</b> {close:.2f} EUR</p>
            <p><b>SMA20:</b> {sma20:.2f}</p>
            <p><b>SMA200:</b> {sma200:.2f}</p>

            <h3>Signal: {signal}</h3>

            <p><i>Generated: {datetime.now()}</i></p>
        </div>
    </body>
    </html>
    """

    with open("signal.html", "w", encoding="utf-8") as f:
        f.write(html)


def main():
    data = get_data()
    data = add_sma(data)

    # 🔥 KLUCZ: usuwamy dzisiejszy dzień (niezamknięta świeca)
    today = pd.Timestamp.today().normalize()
    data = data[data.index < today]

    data = data.dropna()





    last = data.iloc[-1]

    date = last.name.date()
    close = float(last["Close"])
    sma20 = float(last["SMA20"])
    sma200 = float(last["SMA200"])

    signal = generate_signal(close, sma20, sma200)

    save_html(date, close, sma20, sma200, signal)

    print(f"OK -> signal.html (REAL closed: {date})")


if __name__ == "__main__":
    main()
    
