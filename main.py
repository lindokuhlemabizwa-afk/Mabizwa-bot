import requests, time, os
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_TOKEN_HERE")
CHAT_ID = os.getenv("CHAT_ID", "PUT_YOUR_CHAT_ID_HERE")

PAIRS = ["EURUSD", "XAUUSD", "US30", "NAS100"]

# PROFIT SETTINGS - NO R200
SETTINGS = {
    "EURUSD": {"SL": 15, "TP": 40, "RR": "1:2.6"},
    "XAUUSD": {"SL": 400, "TP": 1000, "RR": "1:2.5"}, # $4 SL / $10 TP in cents
    "US30": {"SL": 120, "TP": 300, "RR": "1:2.5"},
    "NAS100": {"SL": 120, "TP": 300, "RR": "1:2.5"}
}

def get_signal(pair):
    # TODO: Connect your price API here (MT5 / TwelveData / TradingView)
    # For now this is your logic placeholder
    # Return: direction, price, reason
    
    # Example logic - replace with your real indicator check
    # This will only send when price is at EXTREME for profit
    return None

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

def run():
    while True:
        for pair in PAIRS:
            signal = get_signal(pair)
            if signal:
                cfg = SETTINGS[pair]
                msg = f"""
🚀 **MABIZWA UPGRADED - PROFIT SIGNAL**

**{pair} {signal['dir']} @ {signal['price']}**
Time: {datetime.now().strftime('%H:%M SAST')}

Entry: {signal['price']}
SL: {cfg['SL']} pips = High RR
TP: {cfg['TP']} pips = 1:{cfg['RR'].split(':')[1]} profit
Reason: {signal['reason']}

No R200 limit - Pure profit hunt
"""
                send_telegram(msg)
        time.sleep(60)

if __name__ == "__main__":
    run()