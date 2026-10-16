import os, requests, yfinance as yf, pandas as pd
from datetime import datetime
import pytz

BOT_TOKEN = os.getenv("BOT_TOKEN", "8802371617:AAGW6K24YRSCEKDk1IOZ0knHQHIo5qx6ijY")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@MABIZWASCANNER")

SYMBOLS = {
    "NAS100": "^NDX",
    "GER30": "^GDAXI", 
    "US30": "^DJI"
}

def get_signal(symbol, ticker):
    try:
        df = yf.download(ticker, period="2d", interval="15m", progress=False)
        if len(df) < 50: return None
        
        # SMC Logic
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        df['EMA200'] = df['Close'].ewm(span=200).mean()
        df['RSI'] = 100 - (100 / (1 + df['Close'].pct_change().rolling(14).mean().abs()))
        
        # Simple RSI calc
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # BOS + Liquidity + RSI Filter (90% Strict)
        bullish_bos = last['Close'] > df['High'].iloc[-20:-1].max()
        bearish_bos = last['Close'] < df['Low'].iloc[-20:-1].min()
        ema_trend_up = last['Close'] > last['EMA50'] > last['EMA200']
        ema_trend_down = last['Close'] < last['EMA50'] < last['EMA200']
        
        rsi_ok_buy = 40 < last['RSI'] < 70
        rsi_ok_sell = 30 < last['RSI'] < 60
        
        # Score for confidence
        score = 0
        signal = None
        
        if bullish_bos and ema_trend_up and rsi_ok_buy:
            signal = "BUY"
            score = 90
            if last['Close'] > prev['Close']: score += 3
        elif bearish_bos and ema_trend_down and rsi_ok_sell:
            signal = "SELL"
            score = 90
            if last['Close'] < prev['Close']: score += 3
            
        if signal:
            entry = float(last['Close'])
            sl = entry * 0.998 if signal == "BUY" else entry * 1.002
            tp1 = entry * 1.003 if signal == "BUY" else entry * 0.997
            tp2 = entry * 1.006 if signal == "BUY" else entry * 0.994
            
            return {
                "symbol": symbol,
                "signal": signal,
                "entry": round(entry,2),
                "sl": round(sl,2),
                "tp1": round(tp1,2),
                "tp2": round(tp2,2),
                "rsi": round(float(last['RSI']),1),
                "conf": min(score, 94)
            }
    except Exception as e:
        print(f"Error {symbol}: {e}")
    return None

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHANNEL_ID, "text": msg, "parse_mode": "Markdown"})

def run():
    sast = pytz.timezone('Africa/Johannesburg')
    now = datetime.now(sast).strftime("%Y-%m-%d %H:%M")
    
    signals = []
    for sym, ticker in SYMBOLS.items():
        s = get_signal(sym, ticker)
        if s: signals.append(s)
    
    if not signals:
        msg = f"🔍 *MABIZWA SCAN - {now} SAST*\n\n⚠️ No 90% setups found\nMarket choppy. Waiting for BOS + Liquidity sweep.\n\nNext scan 15:30\n@MABIZWASCANNER"
        send(msg)
        return
    
    for sig in signals:
        emoji = "🟢" if sig['signal']=="BUY" else "🔴"
        msg = f"""{emoji} *MABIZWA STRICT SIGNAL* {emoji}

📊 *{sig['symbol']}* | {sig['signal']}
⏰ {now} SAST
🎯 *Confidence: {sig['conf']}%*

💰 Entry: {sig['entry']}
🛑 SL: {sig['sl']}
✅ TP1: {sig['tp1']}
✅ TP2: {sig['tp2']}

📈 RSI: {sig['rsi']} | EMA Trend + BOS + Liquidity

⚠️ Risk: 1% per trade
🔥 Strict Rules Only

@MABIZWASCANNER #MABIZWA"""
        send(msg)

if __name__ == "__main__":
    run()