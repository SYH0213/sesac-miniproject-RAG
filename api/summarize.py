import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def summarize_text(docs):
    """
    Summarize the text using OpenAI GPT-4o-mini model.

    Args:
        docs: The documents to summarize.

    Returns:
        The summarized text.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)

    prompt_template = """Write a concise summary of the following:
    {text}
    CONCISE SUMMARY IN KOREAN:"""
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])

    chain = load_summarize_chain(llm, chain_type="stuff", prompt=PROMPT)
    summary = chain.run(docs)

    return summary