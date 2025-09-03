import os
import requests
from dotenv import load_dotenv

load_dotenv()

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

def search_naver_news(query: str, sort: str = "sim", display: int = 10, start: int = 1):
    """
    Search for news articles on Naver News.

    Args:
        query: The search query.
        sort: Sort order (sim: similarity, date: date).
        display: Number of results to display (10-50).
        start: Start index of the results (1-1000).

    Returns:
        A list of news articles, where each article is a dictionary with 'title' and 'link'.
    """
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {"query": query, "sort": sort, "display": display, "start": start}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()
    articles = [
        {"title": item["title"], "link": item["link"], "description": item["description"]}
        for item in data["items"]
    ]

    return articles
