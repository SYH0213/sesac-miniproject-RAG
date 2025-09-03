import fitz  # PyMuPDF
import os

def extract_pdf_content(pdf_path, output_image_dir="extracted_images"):
    try:
        document = fitz.open(pdf_path)
        
        # Create directory for images if it doesn't exist
        if not os.path.exists(output_image_dir):
            os.makedirs(output_image_dir)

        for page_num in range(min(18, len(document))):
            page = document.load_page(page_num)
            
            # Extract text
            text = page.get_text()
            print(f"--- Page {page_num + 1} Text ---")
            print(text)
            print("\n")

            # Extract images
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = document.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_filename = os.path.join(output_image_dir, f"page{page_num + 1}_img{img_index}.{image_ext}")
                with open(image_filename, "wb") as img_file:
                    img_file.write(image_bytes)
                print(f"Saved image: {image_filename}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    pdf_file = "data/gemini-2.5-tech.pdf"
    extract_pdf_content(pdf_file)
