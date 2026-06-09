import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
from datetime import datetime

GMAIL_USER  = os.environ['GMAIL_USER']
GMAIL_PASS  = os.environ['GMAIL_APP_PASSWORD']
TO_EMAIL    = os.environ['TO_EMAIL']
WA_PHONE    = os.environ['WA_PHONE']
WA_APIKEY   = os.environ['WA_APIKEY']
ENABLE_WHATSAPP = False

def get_ibja_rates():
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get('https://ibjarates.com/', headers=headers, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')

    rates = {}
    rows = soup.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 2:
            label = cols[0].get_text(strip=True)
            value = cols[1].get_text(strip=True).replace(',', '')
            try:
                rates[label] = float(value)
            except:
                pass

    return {
        'gold_24k_10g':  rates.get('Gold 999', 0),   # per 10g
        'gold_22k_10g':  rates.get('Gold 916', 0),   # per 10g
        'gold_18k_10g':  rates.get('Gold 750', 0),   # per 10g
        'silver_10g':    rates.get('Silver 999', 0), # per 10g (but in /kg on site)
        'gold_24k_1g':   round(rates.get('Gold 999', 0) / 10, 2),
        'gold_22k_1g':   round(rates.get('Gold 916', 0) / 10, 2),
        'gold_18k_1g':   round(rates.get('Gold 750', 0) / 10, 2),
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

def change_line(today, last, label):
    if not last:
        return "First run — no previous data"
    change    = today - last
    pct       = (change / last) * 100
    direction = "INCREASED ▲" if change > 0 else "DECREASED ▼" if change < 0 else "UNCHANGED ▬"
    tomorrow  = "may go UP 📈" if change > 0 else "may go DOWN 📉" if change < 0 else "may stay STABLE ➡️"
    return (
        f"Change : {'+' if change > 0 else ''}₹{change:.2f} ({pct:+.2f}%) — {direction}\n"
        f"Tomorrow's {label} rate {tomorrow}"
    )

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
        print("Weekend — IBJA closed. Skipping.")
        return

    now   = datetime.now().strftime("%d %b %Y, %I:%M %p")
    rates = get_ibja_rates()

    last_gold   = read_last_price('last_gold.txt')
    last_silver = read_last_price('last_silver.txt')

    gold_chg   = change_line(rates['gold_22k_1g'], last_gold,   'Gold')
    silver_chg = change_line(rates['silver_10g'],  last_silver, 'Silver')

    msg = f"""📊 IBJA Metal Rates — {now}
(Source: India Bullion & Jewellers Association)

{'='*40}
🥇 GOLD
{'='*40}
24K (999) per 1g  : ₹{rates['gold_24k_1g']:>10,.2f}
22K (916) per 1g  : ₹{rates['gold_22k_1g']:>10,.2f}  ← Jewellery
18K (750) per 1g  : ₹{rates['gold_18k_1g']:>10,.2f}

24K per 10g       : ₹{rates['gold_24k_10g']:>10,.2f}
22K per 10g       : ₹{rates['gold_22k_10g']:>10,.2f}  ← Jewellery
18K per 10g       : ₹{rates['gold_18k_10g']:>10,.2f}

{gold_chg}

{'='*40}
🥈 SILVER
{'='*40}
999 per 10g       : ₹{rates['silver_10g']:>10,.2f}

{silver_chg}
"""

    print(msg)
    send_email(f"IBJA Metal Alert — {now}", msg)

    if ENABLE_WHATSAPP:
        send_whatsapp(msg)

    save_price('last_gold.txt',   rates['gold_22k_1g'])
    save_price('last_silver.txt', rates['silver_10g'])

main()
