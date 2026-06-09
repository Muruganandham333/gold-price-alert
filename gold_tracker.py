import requests
import smtplib
from email.mime.text import MIMEText
import os
from datetime import datetime

GMAIL_USER  = os.environ['GMAIL_USER']
GMAIL_PASS  = os.environ['GMAIL_APP_PASSWORD']
TO_EMAIL    = os.environ['TO_EMAIL']
WA_PHONE    = os.environ['WA_PHONE']
WA_APIKEY   = os.environ['WA_APIKEY']
ENABLE_WHATSAPP = False  # set True once Callmebot is ready

TROY_OZ_TO_GRAM = 31.1035

def get_price(symbol):
    r = requests.get(f'https://api.gold-api.com/price/{symbol}/INR', timeout=15)
    r.raise_for_status()
    data = r.json()
    price_per_oz = float(data['price'])
    return {
        'per_oz':       round(price_per_oz, 2),
        'per_gram_24k': round(price_per_oz / TROY_OZ_TO_GRAM, 2),
        'per_gram_22k': round((price_per_oz / TROY_OZ_TO_GRAM) * 0.9167, 2),
        'per_10g_24k':  round((price_per_oz / TROY_OZ_TO_GRAM) * 10, 2),
        'per_10g_22k':  round((price_per_oz / TROY_OZ_TO_GRAM) * 0.9167 * 10, 2),
    }

def read_last_price(filename):
    try:
        with open(filename, 'r') as f:
            return float(f.read().strip())
    except:
        return None

def save_price(filename, price):
    with open(filename, 'w') as f:
        f.write(str(price))

def price_summary(label, today, last):
    if last:
        change    = today['per_gram_24k'] - last
        pct       = (change / last) * 100
        direction = "INCREASED ▲" if change > 0 else "DECREASED ▼" if change < 0 else "UNCHANGED ▬"
        tomorrow  = "may go UP 📈" if change > 0 else "may go DOWN 📉" if change < 0 else "may stay STABLE ➡️"
        change_line = f"Change   : {'+' if change > 0 else ''}₹{change:.2f} ({pct:+.2f}%) — {direction}"
        tomorrow_line = f"Tomorrow's {label} rate {tomorrow}"
    else:
        change_line   = "Change   : First run — no previous data"
        tomorrow_line = ""

    return (
        f"{'='*35}\n"
        f"🪙 {label}\n"
        f"{'='*35}\n"
        f"24K per gram : ₹{today['per_gram_24k']:,.2f}\n"
        f"22K per gram : ₹{today['per_gram_22k']:,.2f}\n"
        f"24K per 10g  : ₹{today['per_10g_24k']:,.2f}\n"
        f"22K per 10g  : ₹{today['per_10g_22k']:,.2f}\n"
        f"Per oz       : ₹{today['per_oz']:,.2f}\n\n"
        f"{change_line}\n"
        f"{tomorrow_line}\n"
    )

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From']    = GMAIL_USER
    msg['To']      = TO_EMAIL
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
        s.login(GMAIL_USER, GMAIL_PASS)
        s.send_message(msg)

def send_whatsapp(message):
    try:
        url = (
            f"https://api.callmebot.com/whatsapp.php"
            f"?phone={WA_PHONE}&text={requests.utils.quote(message)}&apikey={WA_APIKEY}"
        )
        requests.get(url, timeout=10)
        print("WhatsApp sent ✅")
    except Exception as e:
        print(f"WhatsApp skipped ⚠️ — {e}")

def main():
    if datetime.today().weekday() in (5, 6):
        print("Weekend — market closed. Skipping.")
        return

    now = datetime.now().strftime("%d %b %Y, %I:%M %p")

    # Fetch gold and silver
    gold   = get_price('XAU')
    silver = get_price('XAG')

    # Read yesterday's prices
    last_gold   = read_last_price('last_gold.txt')
    last_silver = read_last_price('last_silver.txt')

    # Build message
    gold_summary   = price_summary('GOLD',   gold,   last_gold)
    silver_summary = price_summary('SILVER', silver, last_silver)

    msg = (
        f"📊 Metal Price Alert — {now}\n\n"
        f"{gold_summary}\n"
        f"{silver_summary}"
    )

    print(msg)
    send_email(f"Metal Alert — {now}", msg)

    if ENABLE_WHATSAPP:
        send_whatsapp(msg)

    # Save today's prices
    save_price('last_gold.txt',   gold['per_gram_24k'])
    save_price('last_silver.txt', silver['per_gram_24k'])

main()
