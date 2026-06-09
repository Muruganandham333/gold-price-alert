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
# FETCH COMEX GOLD DATA
# ==========================================

def get_comex_gold_data():

    url = "https://comexlive.org/"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/137.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    session = requests.Session()

    response = session.get(
        url,
        headers=headers,
        timeout=30
    )

    print("STATUS CODE:", response.status_code)

    if response.status_code != 200:

        raise Exception(
            f"COMEX site blocked request "
            f"with status {response.status_code}"
        )

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    rows = soup.find_all("tr")

    for row in rows:

        cols = row.find_all("td")

        if len(cols) >= 4:

            symbol = cols[0].get_text(strip=True)

            if "COMEX Gold" in symbol:

                price = cols[1].get_text(strip=True)
                change = cols[2].get_text(strip=True)
                change_pct = cols[3].get_text(strip=True)

                return {
                    "price": price,
                    "change": change,
                    "change_pct": change_pct
                }

    raise Exception(
        "COMEX Gold row not found"
    )

# ==========================================
# MARKET ANALYSIS
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

        smtp.login(
            GMAIL_USER,
            GMAIL_PASS
        )

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

Percentage Change:
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

Prediction based on COMEX trend.

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
