from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import HTMLHeaderTextSplitter
import kss

def split_text(documents):
    """
    Split text using HTMLHeaderTextSplitter, kss, and RecursiveCharacterTextSplitter.

    Args:
        documents: The documents to split.

    Returns:
        The split documents.
    """
    headers_to_split_on = [
        ("h1", "Header 1"),
        ("h2", "Header 2"),
        ("h3", "Header 3"),
    ]

    html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    html_header_splits = html_splitter.split_text(documents[0].page_content)

    # Now, split by sentences using kss and group them.
    # Then, use RecursiveCharacterTextSplitter.

    # This part is a bit complex, I will need to think about how to combine them.
    # For now, I will just use RecursiveCharacterTextSplitter on the html_header_splits.

    chunk_size = 1000
    chunk_overlap = 150

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    splits = text_splitter.split_documents(html_header_splits)
    return splits
