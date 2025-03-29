import os
import requests
import json
from dotenv import load_dotenv
from discord_webhook import DiscordWebhook

load_dotenv()
API_KEY = os.getenv("API_KEY")

def fetch_news(query="cyberattack"):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching news: {response.status_code}")
        return None
    
def load_keywords():
    try:
        with open("keywords.json", "r") as file:
            keywords = json.load(file)
            return keywords
    except FileNotFoundError:
        print("keywords.json not found. Please create it.")
        return []
    except json.JSONDecodeError:
        print("Error decoding keywords.json. Please check the file format.")
        return []

def classify_severity(headline, keywords):
    for level in ["level_5", "level_4", "level_3", "level_2"]:
        for keyword in keywords[level]:
            if keyword.lower() in headline.lower():
                return int(level.split("_")[1])
    return 1

def send_alert(headline, severity):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if webhook_url:
        webhook = DiscordWebhook(url=webhook_url, content=f"**Severity Level: {severity}**\n{headline}")
        response = webhook.execute()
        if response.status_code == 200:
            print("Alert sent successfully.")
        else:
            print(f"Failed to send alert: {response.status_code}")
    else:
        print("No Discord webhook URL provided. Alert not sent.")

def main():
    keywords = load_keywords()
    if not keywords:
        print("No keywords loaded. Exiting.")
        return

    news_data = fetch_news("earthquake")
    if news_data and "articles" in news_data:
        for article in news_data["articles"]:
            headline = article["title"]
            severity = classify_severity(headline, keywords)
            if severity >= 3:  # Adjust this threshold as needed
                send_alert(headline, severity)
    else:
        print("No articles found or error in fetching news data.")
if __name__ == "__main__":
    main()