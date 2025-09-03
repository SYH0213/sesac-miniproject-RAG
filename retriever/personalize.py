from data.store import get_tag_frequency
from api.naver_search import search_naver_news

MIN_TAG_COUNT = 10  # Minimum number of tags to start recommendations

def get_personalized_recommendations():
    """
    Get personalized news recommendations based on tag frequency.

    Returns:
        A list of recommended articles, or a message if there is not enough data.
    """
    tag_frequency = get_tag_frequency(limit=5)

    if not tag_frequency or sum([count for _, count in tag_frequency]) < MIN_TAG_COUNT:
        return "Not enough data for personalized recommendations yet. Keep using the app!"

    top_tags = [tag for tag, _ in tag_frequency]

    recommended_articles = []
    for tag in top_tags:
        # Avoid duplicate articles
        articles = search_naver_news(tag)
        for article in articles:
            if article not in recommended_articles:
                recommended_articles.append(article)
    
    return recommended_articles
