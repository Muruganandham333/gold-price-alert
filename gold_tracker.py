import requests
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
GOLDAPI_KEY = os.environ['GOLD_API_KEY']   # <-- Your GoldAPI.io key

# ==========================================
# FETCH GOLD DATA (GoldAPI.io)
# ==========================================

def get_gold_data():
    url = "https://www.goldapi.io/api/XAU/INR"
    headers = {
        "x-access-token": GOLDAPI_KEY,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    return {
        "price": str(data["price"]),
        "change": str(data["ch"]),
        "change_pct": str(data["chp"]) + "%"
    }

# ==========================================
# MARKET ANALYSIS
# ==========================================

def analyze_market(change_percent):
    pct = float(change_percent.replace("%", "").replace("+", ""))

    if pct <= -1.5:
        sentiment = "🔴 Strong Bearish"
        prediction = "📉 Tomorrow Indian gold price likely to DECREASE strongly"
        probability = "80%"
    elif pct <= -0.5:
        sentiment = "🟠 Bearish"
        prediction = "⬇️ Tomorrow Indian gold price may DECREASE"
        probability = "65%"
    elif pct < 0:
        sentiment = "🟡 Slight Bearish"
        prediction = "↘️ Tomorrow Indian gold price slightly bearish"
        probability = "55%"
    elif pct >= 1.5:
        sentiment = "🟢 Strong Bullish"
        prediction = "📈 Tomorrow Indian gold price likely to INCREASE strongly"
        probability = "80%"
    elif pct >= 0.5:
        sentiment = "🟢 Bullish"
        prediction = "⬆️ Tomorrow Indian gold price may INCREASE"
        probability = "65%"
    else:
        sentiment = "⚪ Neutral"
        prediction = "➡️ Tomorrow Indian gold price may stay STABLE"
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

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_PASS)
        smtp.send_message(msg)

# ==========================================
# MAIN
# ==========================================

def main():
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")

    gold = get_gold_data()
    analysis = analyze_market(gold["change_pct"])

    msg = f"""
📊 GOLD MARKET ALERT
{now}

======================================
🌍 GOLDAPI.IO LIVE DATA
======================================

Current Price:
{gold['price']} INR

Today's Change:
{gold['change']} INR

Percentage Change:
{gold['change_pct']}

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

Prediction based on GoldAPI trend.

This is NOT financial advice.
"""

    print(msg)
    send_email(f"Gold Prediction Alert - {now}", msg)

# ==========================================
# START
# ==========================================

if __name__ == "__main__":
    main()
