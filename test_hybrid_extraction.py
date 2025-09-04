import fitz  # PyMuPDF
import pandas as pd
import os

def extract_page_content_hybrid(page):
    """
    Extracts both text and tables from a PyMuPDF page object,
    attempting to maintain their vertical order.
    """
    # 1. Find all tables on the page
    tables = page.find_tables()

    # 2. Get all text blocks on the page
    all_blocks = page.get_text("blocks")

    # 3. Create a list of all items (text blocks and tables) with their vertical position
    page_items = []
    for block in all_blocks:
        # item: (y0, type, content)
        # y0 is the vertical position, used for sorting
        page_items.append((block[1], "text", block[4]))

    for table in tables:
        # item: (y0, type, content)
        page_items.append((table.bbox[1], "table", table))

    # 4. Sort items by their vertical position (y0)
    page_items.sort(key=lambda item: item[0])

    # 5. Process sorted items and handle table text duplication
    output_content = []
    table_bboxes = [fitz.Rect(t.bbox) for t in tables]
    processed_text_in_tables = set()

    for y0, item_type, item_content in page_items:
        if item_type == "text":
            # Check if this text block is inside any table's bounding box
            block_rect = fitz.Rect([b for b in all_blocks if b[1] == y0 and b[4] == item_content][0][:4])
            is_in_table = any(bbox.intersects(block_rect) for bbox in table_bboxes)
            
            # If the text is not part of a table, add it to the output
            if not is_in_table:
                output_content.append(item_content)

        elif item_type == "table":
            # Extract table data, convert to DataFrame, then to Markdown
            table_data = item_content.extract()
            if table_data:
                # Use first row as header
                header = table_data[0]
                # Clean up header: replace None and newlines
                cleaned_header = [str(h).replace('\n', ' ') if h is not None else '' for h in header]
                
                df = pd.DataFrame(table_data[1:], columns=cleaned_header)
                output_content.append(df.to_markdown(index=False))
            output_content.append("\n") # Add a newline after the table

    return "\n".join(output_content)


# --- Main execution ---
if __name__ == "__main__":
    # Define paths
    pdf_path = "data/gemini-2.5-tech_1-10.pdf"
    output_path = "hybrid_extraction_output.md"
    page_to_process = 1  # Process Page 2 (0-indexed)

    print(f"Starting hybrid extraction for page {page_to_process + 1} of '{pdf_path}'...")

    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at '{pdf_path}'")
    else:
        try:
            # Open the PDF
            doc = fitz.open(pdf_path)
            if page_to_process < len(doc):
                page = doc[page_to_process]

                # Get the hybrid content
                final_content = extract_page_content_hybrid(page)

                # Write to output file
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(f"# Hybrid Extraction Output for Page {page_to_process + 1}\n\n")
                    f.write(final_content)

                print(f"Successfully extracted content from page {page_to_process + 1} to '{output_path}'")
            else:
                print(f"Error: Page number {page_to_process} is out of range. The document has {len(doc)} pages.")
            doc.close()

        except Exception as e:
            print(f"An error occurred: {e}")
