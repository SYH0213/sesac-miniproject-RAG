from langchain_community.document_loaders import WebBaseLoader

def load_article(url: str):
    """
    Load article from a URL.

    Args:
        url: The URL of the article.

    Returns:
        The loaded documents.
    """
    loader = WebBaseLoader(url)
    docs = loader.load()
    return docs
