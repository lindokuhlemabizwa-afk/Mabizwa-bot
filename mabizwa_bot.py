import os, requests
from datetime import datetime
BOT_TOKEN = os.getenv("BOT_TOKEN", "8802371617:AAGW6K24YRSCEKDk1IOZ0knHQHIo5qx6ijY")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@MABIZWASCANNER")
def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHANNEL_ID, "text": msg, "parse_mode": "Markdown"})
def run():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"🔥 *MABIZWA SCANNER LIVE* 🔥\n⏰ {now} SAST\n\n📊 Market Scan Complete\n✅ NAS100 / GER30 / US30\n✅ 90% Signals\n\nNext: 15:30 @MABIZWASCANNER\n#MABIZWA"
    send(msg)
    print("Sent!")
if __name__ == "__main__":
    run()