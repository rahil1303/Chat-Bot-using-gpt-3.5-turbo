import requests

NEWS_API_KEY = "6f61c4536a214fc287ca31f6125b65b2"

NEWS_API_URL = "https://newsapi.org/v2/everything"

def get_news(query):
    params = {
        'q': query,
        'apiKey': NEWS_API_KEY,
        'sortBy': 'relevancy',
        'language': 'en'
    }
    response = requests.get(NEWS_API_URL, params=params)
    if response.status_code == 200:
        news_data = response.json()
        if news_data['totalResults'] > 0:
            top_article = news_data['articles'][0]
            return f"Latest news on {query}: {top_article['title']}. Read more: {top_article['url']}"
        else:
            return None
    else:
        return None

