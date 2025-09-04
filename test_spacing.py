import pdfplumber
import os

# Define paths
pdf_path = "data/gemini-2.5-tech.pdf"
output_path = "spacing_test_output.md"



output_content = []

try:
    with pdfplumber.open(pdf_path) as pdf:
        # Process only the first page
        page = pdf.pages[0]

        # --- Test 1: Default settings ---
        output_content.append("# Test 1: Default `extract_text()`")
        default_text = page.extract_text()
        output_content.append("```text")
        output_content.append(default_text)
        output_content.append("```")
        output_content.append("\n---\n")


        # --- Test 2: Increased x_tolerance ---
        # The `x_tolerance` parameter merges words separated by a horizontal distance less than this value.
        # Default is 1. Increasing it slightly might help combine characters into words correctly.
        output_content.append("# Test 2: `extract_text(x_tolerance=3)`")
        tolerant_text = page.extract_text(x_tolerance=3)
        output_content.append("```text")
        output_content.append(tolerant_text)
        output_content.append("```")
        output_content.append("\n---\n")

        # --- Test 3: Using keep_blank_chars ---
        output_content.append("# Test 3: `extract_text(keep_blank_chars=True)`")
        keep_blanks_text = page.extract_text(keep_blank_chars=True)
        output_content.append("```text")
        output_content.append(keep_blanks_text)
        output_content.append("```")


    # Write all content to the markdown file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_content))

    print(f"Successfully created '{output_path}' with test results.")

except Exception as e:
    print(f"An error occurred: {e}")
