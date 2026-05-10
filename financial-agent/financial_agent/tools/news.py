import os
from newsapi import NewsApiClient
from dotenv import load_dotenv

load_dotenv()


def get_company_news(ticker: str, company_name: str, days_back: int = 7) -> list[dict]:
    """
    Devuelve las noticias más recientes sobre una empresa.
    Necesitamos tanto el ticker como el nombre porque NewsAPI busca
    por texto, no por ticker. 'AAPL' no encuentra nada — 'Apple' sí.
    """
    api = NewsApiClient(api_key=os.getenv("NEWSAPI_KEY"))

    from datetime import datetime, timedelta
    date_from = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    response = api.get_everything(
        q=company_name,
        from_param=date_from,
        language="en",
        sort_by="relevancy",
        page_size=10,
    )

    if response["status"] != "ok":
        return []

    articles = []
    for article in response["articles"]:
        articles.append({
            "title": article["title"],
            "source": article["source"]["name"],
            "published_at": article["publishedAt"],
            "description": article["description"],
            "url": article["url"],
        })

    return articles