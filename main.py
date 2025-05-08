from news_service import get_technology_news

if __name__ == "__main__":
    news = get_technology_news()
    if news:
        print(news)