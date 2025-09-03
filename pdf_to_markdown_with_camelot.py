import camelot
import pdfplumber # For text extraction

def convert_pdf_to_markdown_camelot(pdf_path, output_md_path):
    markdown_content = []
    
    # Use pdfplumber for text extraction
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            markdown_content.append(f"# Page {i + 1}\n\n")
            
            # Extract text
            text = page.extract_text()
            if text:
                markdown_content.append(text)
                markdown_content.append("\n\n")

            # Extract tables using camelot
            # You might need to adjust flavor ('lattice' or 'stream') and table_areas
            # based on your PDF's table structure.
            try:
                tables = camelot.read_pdf(pdf_path, pages=str(i+1), flavor='lattice') # Try 'lattice' first
                if not tables: # If lattice doesn't find, try 'stream'
                    tables = camelot.read_pdf(pdf_path, pages=str(i+1), flavor='stream')

                for table in tables:
                    df = table.df
                    # Convert pandas DataFrame to Markdown table
                    markdown_content.append(df.to_markdown(index=False))
                    markdown_content.append("\n\n") # Add a newline after each table

            except Exception as e:
                markdown_content.append(f"<!-- Could not extract tables on page {i+1} with camelot: {e} -->\n\n")

            markdown_content.append("\n---\n\n") # Separator between pages

    with open(output_md_path, "w", encoding="utf-8") as md_file:
        md_file.write("".join(markdown_content))
    print(f"Successfully converted '{pdf_path}' to '{output_md_path}' using camelot.")

if __name__ == "__main__":
    pdf_file = "data/gemini-2.5-tech.pdf"
    output_markdown_file = "output_camelot.md"
    convert_pdf_to_markdown_camelot(pdf_file, output_markdown_file)
