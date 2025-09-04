import pdfplumber

def convert_pdf_to_markdown_pdfplumber(pdf_path, output_md_path):
    markdown_content = []
    with pdfplumber.open(pdf_path) as pdf:
        for i in range(min(18, len(pdf.pages))):
            page = pdf.pages[i]
            markdown_content.append(f"# Page {i + 1}\n\n")
            
            # Extract text
            text = page.extract_text()
            if text:
                markdown_content.append(text)
                markdown_content.append("\n\n")
            
            # Extract tables
            tables = page.extract_tables()
            for table in tables:
                # Ensure all elements are strings for header
                header = [str(cell) if cell is not None else "" for cell in table[0]]
                markdown_content.append("| " + " | ".join(header) + " |\n")
                markdown_content.append("|---" * len(header) + "|\n")
                for row in table[1:]:
                    # Ensure all elements are strings for data rows
                    row_str = [str(cell) if cell is not None else "" for cell in row]
                    markdown_content.append("| " + " | ".join(row_str) + " |\n")
                markdown_content.append("\n") # Add a newline after each table

            markdown_content.append("\n---\n\n") # Separator between pages

    with open(output_md_path, "w", encoding="utf-8") as md_file:
        md_file.write("".join(markdown_content))
    print(f"Successfully converted '{pdf_path}' to '{output_md_path}' using pdfplumber.")

if __name__ == "__main__":
    pdf_file = "data/gemini-2.5-tech.pdf"
    output_markdown_file = "output_pdfplumber.md"
    convert_pdf_to_markdown_pdfplumber(pdf_file, output_markdown_file)
