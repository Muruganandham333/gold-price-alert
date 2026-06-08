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

TROY_OZ_TO_GRAM = 31.1035

def get_gold_price_inr():
    r = requests.get('https://api.gold-api.com/price/XAU/INR', timeout=15)
    r.raise_for_status()
    data = r.json()
    price_per_oz_inr  = float(data['price'])
    price_per_gram    = round(price_per_oz_inr / TROY_OZ_TO_GRAM, 2)
    price_per_10gram  = round(price_per_gram * 10, 2)
    return {
        'per_oz':    price_per_oz_inr,
        'per_gram':  price_per_gram,
        'per_10gram': price_per_10gram,
    }

def read_last_price():
    try:
        with open('last_price.txt', 'r') as f:
            return float(f.read().strip())
    except:
        return None

def save_price(price):
    with open('last_price.txt', 'w') as f:
        f.write(str(price))

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
        print("Weekend — gold market closed. Skipping.")
        return

    today = get_gold_price_inr()
    last  = read_last_price()
    now   = datetime.now().strftime("%d %b %Y, %I:%M %p")

    if last:
        change    = today['per_gram'] - last
        pct       = (change / last) * 100
        direction = "INCREASED ▲" if change > 0 else "DECREASED ▼" if change < 0 else "UNCHANGED ▬"
        tomorrow  = "may go UP 📈" if change > 0 else "may go DOWN 📉" if change < 0 else "may stay STABLE ➡️"

        msg = (
            f"🪙 Gold Price Alert — {now}\n\n"
            f"Per  1g  : ₹{today['per_gram']:,.2f}\n"
            f"Per 10g  : ₹{today['per_10gram']:,.2f}\n"
            f"Per 1 oz : ₹{today['per_oz']:,.2f}\n\n"
            f"Change   : {'+' if change > 0 else ''}₹{change:.2f} ({pct:+.2f}%) — {direction}\n\n"
            f"Tomorrow's gold rate {tomorrow}"
        )
    else:
        msg = (
            f"🪙 Gold tracker started! — {now}\n\n"
            f"Per  1g  : ₹{today['per_gram']:,.2f}\n"
            f"Per 10g  : ₹{today['per_10gram']:,.2f}\n"
            f"Per 1 oz : ₹{today['per_oz']:,.2f}"
        )

    print(msg)
    send_email(f"Gold Alert — {now}", msg)
    send_whatsapp(msg)
    save_price(today['per_gram'])

main()
