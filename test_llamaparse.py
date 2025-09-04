import os
from dotenv import load_dotenv
from llama_parse import LlamaParse

def main():
    """
    Uses LlamaParse to parse a PDF and save the result as a Markdown file.
    """
    # Load environment variables from .env file
    load_dotenv()

    # 1. Check for API Key
    api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    if not api_key:
        print("Error: LLAMA_CLOUD_API_KEY not found in .env file.")
        print("Please add your LlamaCloud API key to the .env file.")
        return

    # Define paths
    pdf_path = "data/gemini-2.5-tech_1-10.pdf"
    output_path = "llamaparse_output_full.md"

    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at '{pdf_path}'")
        return

    print("Starting PDF processing with LlamaParse...")
    print("This may take a few moments as it's an API call...")

    try:
        # 2. Initialize the parser
        # result_type="markdown" ensures the output is clean Markdown
        parser = LlamaParse(result_type="markdown", api_key=api_key)

        # 3. Load and parse the document
        documents = parser.load_data(pdf_path)

        # 4. Concatenate content and save to file
        full_markdown_content = ""
        if documents:
            full_markdown_content = "\n".join([doc.text for doc in documents])

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_markdown_content)

        print(f"Successfully processed the PDF and saved the output to '{output_path}'")
        print("Please check the file to see how LlamaParse handled the tables.")

    except Exception as e:
        print(f"An error occurred during LlamaParse processing: {e}")
        print("Please ensure your API key is valid and you have an internet connection.")

if __name__ == "__main__":
    main()
