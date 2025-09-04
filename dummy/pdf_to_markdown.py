import fitz  # PyMuPDF
import os

def convert_pdf_to_markdown(pdf_path, output_md_path):
    try:
        document = fitz.open(pdf_path)
        markdown_content = []

        for page_num in range(len(document)):
            page = document.load_page(page_num)
            text = page.get_text("text")  # Extract text
            
            markdown_content.append(f"# Page {page_num + 1}\n\n")
            markdown_content.append(text)
            markdown_content.append("\n\n---\n\n") # Separator between pages

        with open(output_md_path, "w", encoding="utf-8") as md_file:
            md_file.write("".join(markdown_content))
        
        print(f"Successfully converted '{pdf_path}' to '{output_md_path}'")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    pdf_file = "data/gemini-2.5-tech.pdf"
    output_markdown_file = "output.md" # Default output file name
    convert_pdf_to_markdown(pdf_file, output_markdown_file)
