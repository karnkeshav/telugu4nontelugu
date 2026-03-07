import fitz  # PyMuPDF
import os
import json

def extract_pages(pdf_path, chapters_json_path, base_output_dir):
    # Load chapters info
    with open(chapters_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        chapters = data.get('chapters', [])

    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return

    # Open the PDF
    doc = fitz.open(pdf_path)
    
    for chapter in chapters:
        chapter_id = chapter.get('id')
        # Skip chapter 1 as it's already done or handle it if needed
        # User asked for 2 to last
        if chapter_id < 2:
            continue
            
        chapter_name = chapter.get('folder')
        start_page = chapter.get('start_page')
        end_page = chapter.get('end_page')
        
        output_dir = os.path.join(base_output_dir, chapter_name, "images")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        print(f"Extracting Chapter {chapter_id}: {chapter.get('name')} (Pages {start_page}-{end_page})")
        
        # start_page and end_page in JSON are 1-indexed, fitz is 0-indexed
        # Also check if the page numbers are within range
        for pg_num in range(start_page, end_page + 1):
            if pg_num > len(doc):
                print(f"Warning: Page {pg_num} is out of range for the PDF.")
                break
                
            page = doc.load_page(pg_num - 1)  # 0-indexed
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scale for better quality
            
            output_filename = f"page_{pg_num:03d}.png"
            output_path = os.path.join(output_dir, output_filename)
            pix.save(output_path)
            # print(f"  Saved {output_filename}")

    doc.close()
    print("Extraction complete!")

if __name__ == "__main__":
    pdf_file = r"c:\Users\keysh\github\telugu4nontelugu\class6\pdf\6th Tel for OM 2025-26.pdf"
    chapters_json = r"c:\Users\keysh\github\telugu4nontelugu\class6\chapters.json"
    output_base = r"c:\Users\keysh\github\telugu4nontelugu\class6"
    
    extract_pages(pdf_file, chapters_json, output_base)
