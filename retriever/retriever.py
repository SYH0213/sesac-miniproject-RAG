from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers import EnsembleRetriever
from langchain.docstore.document import Document
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.retrievers import ContextualCompressionRetriever
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.rankers import CohereRerank
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY") # Assuming Cohere API key is needed for CohereRerank

def create_retriever(articles, query):
    # Convert articles to Document objects for BM25
    bm25_docs = [Document(page_content=article["title"] + " " + article["description"], metadata=article) for article in articles]
    bm25_retriever = BM25Retriever.from_documents(bm25_docs)
    bm25_retriever.k = 30 # Initial k value for BM25 (as per prompt)

    # Create embeddings and Chroma vector store for dense retrieval
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectorstore = Chroma.from_documents(bm25_docs, embeddings)
    dense_retriever = vectorstore.as_retriever(search_kwargs={"k": 30}) # Initial k value for dense retriever

    # Initialize the Ensemble Retriever (1차 Rerank)
    ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, dense_retriever], weights=[0.5, 0.5])

    # 2차 Rerank: Keyword-based Sentence Extraction (This is implicitly handled by the compressor focusing on relevant parts)
    # For explicit keyword extraction, a separate step would be needed before compression.
    # For now, the ContextualCompressionRetriever with LLMChainExtractor will focus on relevant sentences.

    # 3차 Rerank: Cross-encoder Reranking
    # Using CohereRerank as an example. You might need to install cohere-rerank library.
    # compressor = CohereRerank(cohere_api_key=COHERE_API_KEY, top_n=8) # top_n for final rerank (6-8 as per prompt)
    
    # If CohereRerank is not preferred or available, you can use LLMChainExtractor for compression
    # and rely on the LLM to implicitly rerank by focusing on relevant information.
    llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY, temperature=0)
    compressor = LLMChainExtractor.from_llm(llm)

    # Contextual Compression Retriever
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=ensemble_retriever
    )

    # Perform retrieval and compression
    retrieved_docs = compression_retriever.get_relevant_documents(query)
    
    return retrieved_docs
