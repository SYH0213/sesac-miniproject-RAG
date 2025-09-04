import fitz  # PyMuPDF
import os

# Define paths
pdf_path = "data/gemini-2.5-tech_1-10.pdf"  # Updated PDF path
output_path = "pymupdf_test_output.md"

output_content = []

try:
    # Open the PDF file
    with fitz.open(pdf_path) as doc:
        output_content.append(f"# PyMuPDF Output for {os.path.basename(pdf_path)}")
        output_content.append("\n---\n")

        # Process all 10 pages
        for i, page in enumerate(doc):
            text = page.get_text("text")
            output_content.append(f"## Page {i + 1}")
            output_content.append("```text")
            output_content.append(text)
            output_content.append("```")
            output_content.append("\n---\n")

    # Write content to the markdown file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_content))

    print(f"Successfully created '{output_path}' with PyMuPDF test results for all pages.")

except Exception as e:
    if isinstance(e, ModuleNotFoundError):
        print("Error: PyMuPDF is not installed. Please install it by running: pip install PyMuPDF")
    else:
        print(f"An error occurred: {e}")
