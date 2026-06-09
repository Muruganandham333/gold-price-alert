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

def get_gold(symbol='XAU'):
    r = requests.get(f'https://api.gold-api.com/price/{symbol}/INR', timeout=15)
    r.raise_for_status()
    price_per_oz = float(r.json()['price'])
    per_gram     = price_per_oz / TROY_OZ_TO_GRAM
    return {
        'per_oz':       round(price_per_oz, 2),
        'per_gram_24k': round(per_gram, 2),
        'per_gram_22k': round(per_gram * 0.9167, 2),
        'per_gram_18k': round(per_gram * 0.7500, 2),
        'per_10g_24k':  round(per_gram * 10, 2),
        'per_10g_22k':  round(per_gram * 0.9167 * 10, 2),
        'per_10g_18k':  round(per_gram * 0.7500 * 10, 2),
    }

def get_silver(symbol='XAG'):
    r = requests.get(f'https://api.gold-api.com/price/{symbol}/INR', timeout=15)
    r.raise_for_status()
    price_per_oz = float(r.json()['price'])
    per_gram     = price_per_oz / TROY_OZ_TO_GRAM
    return {
        'per_oz':        round(price_per_oz, 2),
        'per_gram_999':  round(per_gram, 2),               # Fine silver
        'per_gram_925':  round(per_gram * 0.925, 2),       # Sterling silver
        'per_gram_800':  round(per_gram * 0.800, 2),       # German silver
        'per_10g_999':   round(per_gram * 10, 2),
        'per_10g_925':   round(per_gram * 0.925 * 10, 2),
        'per_10g_800':   round(per_gram * 0.800 * 10, 2),
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

def change_summary(today_price, last_price, label):
    if last_price:
        change    = today_price - last_price
        pct       = (change / last_price) * 100
        direction = "INCREASED ▲" if change > 0 else "DECREASED ▼" if change < 0 else "UNCHANGED ▬"
        tomorrow  = "may go UP 📈" if change > 0 else "may go DOWN 📉" if change < 0 else "may stay STABLE ➡️"
        return (
            f"Change   : {'+' if change > 0 else ''}₹{change:.2f} "
            f"({pct:+.2f}%) — {direction}\n"
            f"Tomorrow's {label} rate {tomorrow}"
        )
    return "Change   : First run — no previous data"

def send_email(subject, body):
    msg = MIMEText(body, 'plain', 'utf-8')
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

    gold   = get_gold()
    silver = get_silver()

    last_gold   = read_last_price('last_gold.txt')
    last_silver = read_last_price('last_silver.txt')

    gold_change   = change_summary(gold['per_gram_24k'],   last_gold,   'Gold')
    silver_change = change_summary(silver['per_gram_999'], last_silver, 'Silver')

    msg = f"""📊 Metal Price Alert — {now}

{'='*38}
🥇 GOLD (per gram)
{'='*38}
24K (Pure)    : ₹{gold['per_gram_24k']:>10,.2f}
22K (Jewellery): ₹{gold['per_gram_22k']:>10,.2f}
18K (Mixed)   : ₹{gold['per_gram_18k']:>10,.2f}

24K per 10g   : ₹{gold['per_10g_24k']:>10,.2f}
22K per 10g   : ₹{gold['per_10g_22k']:>10,.2f}
18K per 10g   : ₹{gold['per_10g_18k']:>10,.2f}

Per oz        : ₹{gold['per_oz']:>10,.2f}
{gold_change}

{'='*38}
🥈 SILVER (per gram)
{'='*38}
999 Fine      : ₹{silver['per_gram_999']:>10,.2f}
925 Sterling  : ₹{silver['per_gram_925']:>10,.2f}
800 German    : ₹{silver['per_gram_800']:>10,.2f}

999 per 10g   : ₹{silver['per_10g_999']:>10,.2f}
925 per 10g   : ₹{silver['per_10g_925']:>10,.2f}
800 per 10g   : ₹{silver['per_10g_800']:>10,.2f}

Per oz        : ₹{silver['per_oz']:>10,.2f}
{silver_change}
"""

    print(msg)
    send_email(f"Metal Alert — {now}", msg)

    if ENABLE_WHATSAPP:
        send_whatsapp(msg)

    save_price('last_gold.txt',   gold['per_gram_24k'])
    save_price('last_silver.txt', silver['per_gram_999'])

main()
