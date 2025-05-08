import requests
from config import settings


def get_technology_news():
    url = 'https://newsapi.org/v2/top-headlines'
    params = {
        'apiKey': settings.NEWS_API_KEY,
        'category': 'technology,ai,machine learning,data science',
        'language': 'en',
        'pageSize': 10
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error fetching news: {response.status_code}")
        return None

    data = response.json()
    if data['articles']:
        news_texts = []
        for article in data['articles']:
            news_texts.append(f"📰 **Title**: {article['title']}\n📝 *Description*: {article['description']}")
        return "\n\n".join(news_texts)
    else:
        print("No news found.")
        return None

