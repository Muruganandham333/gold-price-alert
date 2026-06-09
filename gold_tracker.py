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
# FETCH IBJA GOLD RATE
# ==========================================

def get_ibja_rates():

    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(
        'https://ibjarates.com/',
        headers=headers,
        timeout=15
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    rates = {}

    rows = soup.find_all('tr')

    for row in rows:

        cols = row.find_all('td')

        if len(cols) >= 2:

            label = cols[0].get_text(strip=True)

            value = (
                cols[1]
                .get_text(strip=True)
                .replace(',', '')
            )

            try:
                rates[label] = float(value)
            except:
                pass

    gold_24k_10g = rates.get('Gold 999', 0)
    gold_22k_10g = rates.get('Gold 916', 0)
    gold_18k_10g = rates.get('Gold 750', 0)

    return {
        'gold_24k_10g': gold_24k_10g,
        'gold_22k_10g': gold_22k_10g,
        'gold_18k_10g': gold_18k_10g,

        'gold_24k_1g': round(gold_24k_10g / 10, 2),
        'gold_22k_1g': round(gold_22k_10g / 10, 2),
        'gold_18k_1g': round(gold_18k_10g / 10, 2)
    }

# ==========================================
# HISTORY FUNCTIONS
# ==========================================

HISTORY_FILE = "gold_history.txt"

def read_history():

    try:

        with open(HISTORY_FILE, 'r') as file:

            lines = file.readlines()

            history = []

            for line in lines:

                line = line.strip()

                if line:
                    history.append(float(line))

            return history

    except:
        return []

def save_today_price(price):

    history = read_history()

    history.append(price)

    # keep only last 7 records
    history = history[-7:]

    with open(HISTORY_FILE, 'w') as file:

        for item in history:
            file.write(f"{item}\n")

# ==========================================
# ANALYSIS LOGIC
# ==========================================

def analyze_gold(current_price, history):

    if len(history) == 0:

        return {
            "change": 0,
            "pct": 0,
            "score": 0,
            "trend": "First Run - No Previous Data",
            "confidence": "LOW",
            "details": [
                "No previous history available"
            ]
        }

    yesterday_price = history[-1]

    change = current_price - yesterday_price

    pct = (change / yesterday_price) * 100

    score = 0

    reasons = []

    # ======================================
    # DAILY MOVEMENT ANALYSIS
    # ======================================

    if change >= 50:

        score += 3
        reasons.append("Strong upward movement detected")

    elif change >= 20:

        score += 2
        reasons.append("Moderate upward movement detected")

    elif change > 0:

        score += 1
        reasons.append("Small upward movement detected")

    elif change <= -50:

        score -= 3
        reasons.append("Strong downward movement detected")

    elif change <= -20:

        score -= 2
        reasons.append("Moderate downward movement detected")

    elif change < 0:

        score -= 1
        reasons.append("Small downward movement detected")

    else:

        reasons.append("No major movement detected")

    # ======================================
    # 3 DAY MOMENTUM
    # ======================================

    if len(history) >= 3:

        avg_3day = sum(history[-3:]) / 3

        if current_price > avg_3day:

            score += 1
            reasons.append("Price above 3-day average")

        else:

            score -= 1
            reasons.append("Price below 3-day average")

    # ======================================
    # FINAL TREND
    # ======================================

    if score >= 3:

        trend = "📈 Tomorrow Gold Rate Likely to INCREASE"
        confidence = "HIGH"

    elif score >= 1:

        trend = "⬆️ Tomorrow Gold Rate Slightly Bullish"
        confidence = "MEDIUM"

    elif score <= -3:

        trend = "📉 Tomorrow Gold Rate Likely to DECREASE"
        confidence = "HIGH"

    elif score <= -1:

        trend = "⬇️ Tomorrow Gold Rate Slightly Bearish"
        confidence = "MEDIUM"

    else:

        trend = "➡️ Tomorrow Gold Rate May Stay Stable"
        confidence = "LOW"

    return {
        "change": change,
        "pct": pct,
        "score": score,
        "trend": trend,
        "confidence": confidence,
        "details": reasons
    }

# ==========================================
# EMAIL FUNCTION
# ==========================================

def send_email(subject, body):

    msg = MIMEText(body, 'plain', 'utf-8')

    msg['Subject'] = subject
    msg['From'] = GMAIL_USER
    msg['To'] = TO_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:

        smtp.login(GMAIL_USER, GMAIL_PASS)

        smtp.send_message(msg)

# ==========================================
# MAIN
# ==========================================

def main():

    # Skip weekends
    if datetime.today().weekday() in (5, 6):

        print("Weekend - Market Closed")

        return

    now = datetime.now().strftime("%d %b %Y, %I:%M %p")

    # Fetch rates
    rates = get_ibja_rates()

    current_price = rates['gold_22k_1g']

    # Read history
    history = read_history()

    # Analyze
    analysis = analyze_gold(current_price, history)

    details_text = '\n- '.join(analysis['details'])

    # Last 3 days
    history_text = ""

    if history:

        recent = history[-3:]

        for index, value in enumerate(recent, start=1):

            history_text += f"Day {index}: ₹{value}\n"

    # Email body
    msg = f"""
📊 GOLD RATE ANALYSIS
{now}

========================================
🥇 CURRENT GOLD RATE
========================================

24K Gold (1g): ₹{rates['gold_24k_1g']}
22K Gold (1g): ₹{rates['gold_22k_1g']}
18K Gold (1g): ₹{rates['gold_18k_1g']}

24K Gold (10g): ₹{rates['gold_24k_10g']}
22K Gold (10g): ₹{rates['gold_22k_10g']}
18K Gold (10g): ₹{rates['gold_18k_10g']}

========================================
📈 MARKET MOVEMENT
========================================

Today's Change:
₹{analysis['change']:+.2f}

Percentage Change:
{analysis['pct']:+.2f}%

Trend Score:
{analysis['score']}

========================================
🔮 TOMORROW PREDICTION
========================================

{analysis['trend']}

Confidence:
{analysis['confidence']}

Reasons:
- {details_text}

========================================
📅 LAST RECORDED PRICES
========================================

{history_text}

========================================
⚠️ DISCLAIMER
========================================

Prediction is based on simple trend analysis.
This is NOT financial advice.
"""

    print(msg)

    # Send email
    send_email(
        f"Gold Prediction Alert - {now}",
        msg
    )

    # Save today's price
    save_today_price(current_price)

# ==========================================
# START
# ==========================================

if __name__ == "__main__":
    main()


