import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def generate_tags(text):
    """
    Generate hashtags for the text using OpenAI GPT-4o-mini model.

    Args:
        text: The text to generate hashtags for.

    Returns:
        A list of hashtags.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)

    prompt_template = """Generate 3 to 6 hashtags for the following text. Exclude common words like 'news' and 'issue'.
    {text}
    HASHTAGS IN KOREAN:"""
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])

    chain = PROMPT | llm
    hashtags_str = chain.invoke({"text": text}).content
    hashtags = [tag.strip() for tag in hashtags_str.split("#") if tag.strip()]

    return hashtags
