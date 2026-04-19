import config
import requests

class NewsModule:
    def __init__(self):
        self.url = f"https://newsapi.org/v2/top-headlines?q=india&apiKey={config.NEWS_KEY}"

    def get_news(self):
        try:
            response = requests.get(self.url, timeout=10)
            data = response.json()
            articles = data.get("articles",[])
            top_articles = articles[:5]
            titles = []
            for article in top_articles:
                titles.append(article["title"])
            return titles
        
        except (requests.exceptions.RequestException, Exception):
            return "Sorry, I couldn't fetch the news right now"
