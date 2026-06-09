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
import json
from datetime import datetime

# =========================================
# ENV VARIABLES
# =========================================

GMAIL_USER = os.environ['GMAIL_USER']
GMAIL_PASS = os.environ['GMAIL_APP_PASSWORD']
TO_EMAIL = os.environ['TO_EMAIL']
GOLD_API_KEY = os.environ['GOLD_API_KEY']

HISTORY_FILE = "gold_history.json"

# =========================================
# FETCH IBJA RATE
# =========================================

def get_ibja_rate():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        "https://ibjarates.com/",
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.find_all("tr")

    rates = {}

    for row in rows:

        cols = row.find_all("td")

        if len(cols) >= 2:

            label = cols[0].get_text(strip=True)

            value = (
                cols[1]
                .get_text(strip=True)
                .replace(",", "")
            )

            try:
                rates[label] = float(value)
            except:
                pass

    gold_22k_10g = rates.get("Gold 916", 0)

    if gold_22k_10g == 0:
        raise Exception("Unable to fetch IBJA Gold Rate")

    return {
        "gold_22k_10g": gold_22k_10g,
        "gold_22k_1g": round(gold_22k_10g / 10, 2)
    }

# =========================================
# GOLD API DATA
# =========================================

def get_gold_api_data():

    headers = {
        "x-access-token": GOLD_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.get(
        "https://www.goldapi.io/api/XAU/USD",
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    return {
        "price": data.get("price", 0),
        "change_percent": data.get("chp", 0),
        "change_price": data.get("chg", 0)
    }

# =========================================
# HISTORY FUNCTIONS
# =========================================

def load_history():

    try:

        with open(HISTORY_FILE, "r") as file:
            return json.load(file)

    except:
        return []

def save_history(price):

    history = load_history()

    history.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "price": price
    })

    history = history[-7:]

    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=2)

# =========================================
# ANALYSIS
# =========================================

def analyze_trend(current_price, history, gold_api):

    score = 0

    reasons = []

    yesterday_price = None

    if history:
        yesterday_price = history[-1]["price"]

    # =====================================
    # LOCAL PRICE MOVEMENT
    # =====================================

    local_change = 0
    local_pct = 0

    if yesterday_price:

        local_change = current_price - yesterday_price

        local_pct = (
            local_change / yesterday_price
        ) * 100

        if local_change > 50:
            score += 3
            reasons.append("Strong local gold rise")

        elif local_change > 20:
            score += 2
            reasons.append("Moderate local gold rise")

        elif local_change > 0:
            score += 1
            reasons.append("Small local gold rise")

        elif local_change < -50:
            score -= 3
            reasons.append("Strong local gold fall")

        elif local_change < -20:
            score -= 2
            reasons.append("Moderate local gold fall")

        elif local_change < 0:
            score -= 1
            reasons.append("Small local gold fall")

    # =====================================
    # INTERNATIONAL GOLD TREND
    # =====================================

    global_change_pct = gold_api["change_percent"]

    if global_change_pct > 1:
        score += 3
        reasons.append("International gold strongly bullish")

    elif global_change_pct > 0.3:
        score += 2
        reasons.append("International gold bullish")

    elif global_change_pct < -1:
        score -= 3
        reasons.append("International gold strongly bearish")

    elif global_change_pct < -0.3:
        score -= 2
        reasons.append("International gold bearish")

    # =====================================
    # MOMENTUM
    # =====================================

    if len(history) >= 3:

        avg3 = (
            sum(item["price"] for item in history[-3:])
            / 3
        )

        if current_price > avg3:
            score += 1
            reasons.append("Above 3-day average")

        else:
            score -= 1
            reasons.append("Below 3-day average")

    # =====================================
    # FINAL TREND
    # =====================================

    confidence = min(abs(score) * 18, 95)

    if score >= 4:
        prediction = "📈 Gold likely to INCREASE tomorrow"

    elif score >= 1:
        prediction = "⬆️ Gold slightly bullish tomorrow"

    elif score <= -4:
        prediction = "📉 Gold likely to DECREASE tomorrow"

    elif score <= -1:
        prediction = "⬇️ Gold slightly bearish tomorrow"

    else:
        prediction = "➡️ Gold may remain stable tomorrow"

    return {
        "prediction": prediction,
        "confidence": confidence,
        "score": score,
        "local_change": local_change,
        "local_pct": local_pct,
        "reasons": reasons
    }

# =========================================
# SEND EMAIL
# =========================================

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

# =========================================
# MAIN
# =========================================

def main():

    now = datetime.now().strftime(
        "%d %b %Y, %I:%M %p"
    )

    ibja = get_ibja_rate()

    gold_api = get_gold_api_data()

    history = load_history()

    analysis = analyze_trend(
        ibja["gold_22k_1g"],
        history,
        gold_api
    )

    reasons_text = "\n- ".join(
        analysis["reasons"]
    )

    history_text = ""

    for item in history[-3:]:

        history_text += (
            f"{item['date']} → "
            f"₹{item['price']}\n"
        )

    msg = f"""
📊 GOLD MARKET ANALYSIS
{now}

======================================
🥇 INDIAN GOLD RATE (IBJA)
======================================

22K Gold (1g):
₹{ibja['gold_22k_1g']}

22K Gold (10g):
₹{ibja['gold_22k_10g']}

======================================
🌍 INTERNATIONAL GOLD
======================================

GoldAPI Price:
${gold_api['price']}

Daily Change:
{gold_api['change_percent']}%

======================================
📈 LOCAL MARKET MOVEMENT
======================================

Today's Change:
₹{analysis['local_change']:+.2f}

Percentage:
{analysis['local_pct']:+.2f}%

Trend Score:
{analysis['score']}

======================================
🔮 TOMORROW PREDICTION
======================================

{analysis['prediction']}

Confidence:
{analysis['confidence']}%

Reasons:
- {reasons_text}

======================================
📅 LAST RECORDED PRICES
======================================

{history_text}

======================================
⚠️ DISCLAIMER
======================================

Trend estimation only.
Not financial advice.
"""

    print(msg)

    send_email(
        f"Gold Prediction Alert - {now}",
        msg
    )

    save_history(
        ibja["gold_22k_1g"]
    )

if __name__ == "__main__":
    main()
