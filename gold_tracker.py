# import requests
# from bs4 import BeautifulSoup
# import smtplib
# from email.mime.text import MIMEText
# import os
# from datetime import datetime

# GMAIL_USER  = os.environ['GMAIL_USER']
# GMAIL_PASS  = os.environ['GMAIL_APP_PASSWORD']
# TO_EMAIL    = os.environ['TO_EMAIL']
# WA_PHONE    = os.environ['WA_PHONE']
# WA_APIKEY   = os.environ['WA_APIKEY']
# ENABLE_WHATSAPP = False

# def get_ibja_rates():
#     headers = {'User-Agent': 'Mozilla/5.0'}
#     r = requests.get('https://ibjarates.com/', headers=headers, timeout=15)
#     r.raise_for_status()
#     soup = BeautifulSoup(r.text, 'html.parser')

#     rates = {}
#     rows = soup.find_all('tr')
#     for row in rows:
#         cols = row.find_all('td')
#         if len(cols) >= 2:
#             label = cols[0].get_text(strip=True)
#             value = cols[1].get_text(strip=True).replace(',', '')
#             try:
#                 rates[label] = float(value)
#             except:
#                 pass

#     return {
#         'gold_24k_10g':  rates.get('Gold 999', 0),   # per 10g
#         'gold_22k_10g':  rates.get('Gold 916', 0),   # per 10g
#         'gold_18k_10g':  rates.get('Gold 750', 0),   # per 10g
#         'silver_10g':    rates.get('Silver 999', 0), # per 10g (but in /kg on site)
#         'gold_24k_1g':   round(rates.get('Gold 999', 0) / 10, 2),
#         'gold_22k_1g':   round(rates.get('Gold 916', 0) / 10, 2),
#         'gold_18k_1g':   round(rates.get('Gold 750', 0) / 10, 2),
#     }

# def read_last_price(filename):
#     try:
#         with open(filename, 'r') as f:
#             return float(f.read().strip())
#     except:
#         return None

# def save_price(filename, price):
#     with open(filename, 'w') as f:
#         f.write(str(price))

# def change_line(today, last, label):
#     if not last:
#         return "First run — no previous data"
#     change    = today - last
#     pct       = (change / last) * 100
#     direction = "INCREASED ▲" if change > 0 else "DECREASED ▼" if change < 0 else "UNCHANGED ▬"
#     tomorrow  = "may go UP 📈" if change > 0 else "may go DOWN 📉" if change < 0 else "may stay STABLE ➡️"
#     return (
#         f"Change : {'+' if change > 0 else ''}₹{change:.2f} ({pct:+.2f}%) — {direction}\n"
#         f"Tomorrow's {label} rate {tomorrow}"
#     )

# def send_email(subject, body):
#     msg = MIMEText(body, 'plain', 'utf-8')
#     msg['Subject'] = subject
#     msg['From']    = GMAIL_USER
#     msg['To']      = TO_EMAIL
#     with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
#         s.login(GMAIL_USER, GMAIL_PASS)
#         s.send_message(msg)

# def send_whatsapp(message):
#     try:
#         url = (
#             f"https://api.callmebot.com/whatsapp.php"
#             f"?phone={WA_PHONE}&text={requests.utils.quote(message)}&apikey={WA_APIKEY}"
#         )
#         requests.get(url, timeout=10)
#         print("WhatsApp sent ✅")
#     except Exception as e:
#         print(f"WhatsApp skipped ⚠️ — {e}")

# def main():
#     if datetime.today().weekday() in (5, 6):
#         print("Weekend — IBJA closed. Skipping.")
#         return

#     now   = datetime.now().strftime("%d %b %Y, %I:%M %p")
#     rates = get_ibja_rates()

#     last_gold   = read_last_price('last_gold.txt')
#     last_silver = read_last_price('last_silver.txt')

#     gold_chg   = change_line(rates['gold_22k_1g'], last_gold,   'Gold')
#     silver_chg = change_line(rates['silver_10g'],  last_silver, 'Silver')

#     msg = f"""📊 IBJA Metal Rates — {now}
# (Source: India Bullion & Jewellers Association)

# {'='*40}
# 🥇 GOLD
# {'='*40}
# 24K (999) per 1g  : ₹{rates['gold_24k_1g']:>10,.2f}
# 22K (916) per 1g  : ₹{rates['gold_22k_1g']:>10,.2f}  ← Jewellery
# 18K (750) per 1g  : ₹{rates['gold_18k_1g']:>10,.2f}

# 24K per 10g       : ₹{rates['gold_24k_10g']:>10,.2f}
# 22K per 10g       : ₹{rates['gold_22k_10g']:>10,.2f}  ← Jewellery
# 18K per 10g       : ₹{rates['gold_18k_10g']:>10,.2f}

# {gold_chg}

# {'='*40}
# 🥈 SILVER
# {'='*40}
# 999 per 10g       : ₹{rates['silver_10g']:>10,.2f}

# {silver_chg}
# """

#     print(msg)
#     send_email(f"IBJA Metal Alert — {now}", msg)

#     if ENABLE_WHATSAPP:
#         send_whatsapp(msg)

#     save_price('last_gold.txt',   rates['gold_22k_1g'])
#     save_price('last_silver.txt', rates['silver_10g'])

# main()

import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
from datetime import datetime

# ==========================================
# ENV VARIABLES
# ==========================================

GMAIL_USER = os.environ['GMAIL_USER']
GMAIL_PASS = os.environ['GMAIL_APP_PASSWORD']
TO_EMAIL = os.environ['TO_EMAIL']

# ==========================================
# FETCH COMEX DATA
# ==========================================

def get_comex_gold_data():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        "https://comexlive.org/",
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.find_all("tr")

    for row in rows:

        text = row.get_text(" ", strip=True)

        if "COMEX Gold" in text:

            cols = row.find_all("td")

            if len(cols) >= 6:

                last_price = cols[1].get_text(strip=True)
                change = cols[2].get_text(strip=True)
                change_pct = cols[3].get_text(strip=True)

                return {
                    "price": last_price,
                    "change": change,
                    "change_pct": change_pct
                }

    raise Exception("Unable to fetch COMEX Gold data")

# ==========================================
# PREDICTION LOGIC
# ==========================================

def analyze_market(change_percent):

    pct = float(
        change_percent
        .replace("%", "")
        .replace("+", "")
    )

    if pct <= -1.5:

        sentiment = "🔴 Strong Bearish"

        prediction = (
            "📉 Tomorrow Indian gold price "
            "likely to DECREASE strongly"
        )

        probability = "80%"

    elif pct <= -0.5:

        sentiment = "🟠 Bearish"

        prediction = (
            "⬇️ Tomorrow Indian gold price "
            "may DECREASE"
        )

        probability = "65%"

    elif pct < 0:

        sentiment = "🟡 Slight Bearish"

        prediction = (
            "↘️ Tomorrow Indian gold price "
            "slightly bearish"
        )

        probability = "55%"

    elif pct >= 1.5:

        sentiment = "🟢 Strong Bullish"

        prediction = (
            "📈 Tomorrow Indian gold price "
            "likely to INCREASE strongly"
        )

        probability = "80%"

    elif pct >= 0.5:

        sentiment = "🟢 Bullish"

        prediction = (
            "⬆️ Tomorrow Indian gold price "
            "may INCREASE"
        )

        probability = "65%"

    else:

        sentiment = "⚪ Neutral"

        prediction = (
            "➡️ Tomorrow Indian gold price "
            "may stay STABLE"
        )

        probability = "50%"

    return {
        "sentiment": sentiment,
        "prediction": prediction,
        "probability": probability
    }

# ==========================================
# SEND EMAIL
# ==========================================

def send_email(subject, body):

    msg = MIMEText(body, "plain", "utf-8")

    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as smtp:

        smtp.login(GMAIL_USER, GMAIL_PASS)

        smtp.send_message(msg)

# ==========================================
# MAIN
# ==========================================

def main():

    now = datetime.now().strftime(
        "%d %b %Y, %I:%M %p"
    )

    comex = get_comex_gold_data()

    analysis = analyze_market(
        comex["change_pct"]
    )

    msg = f"""
📊 GOLD MARKET ALERT
{now}

======================================
🌍 COMEX GOLD LIVE
======================================

Current Price:
{comex['price']}

Today's Change:
{comex['change']}

Change Percentage:
{comex['change_pct']}

======================================
📈 MARKET SENTIMENT
======================================

{analysis['sentiment']}

======================================
🔮 TOMORROW PREDICTION
======================================

{analysis['prediction']}

Chance Probability:
{analysis['probability']}

======================================
⚠️ DISCLAIMER
======================================

Prediction based on COMEX market trend.
This is NOT financial advice.
"""

    print(msg)

    send_email(
        f"Gold Prediction Alert - {now}",
        msg
    )

# ==========================================
# START
# ==========================================

if __name__ == "__main__":
    main()


