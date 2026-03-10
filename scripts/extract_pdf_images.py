import os
import argparse
import fitz  # PyMuPDF

def extract_pages_to_images(pdf_path, output_dir=".", single_page=None, start_page=None, end_page=None):
    """
    Extracts pages from a PDF to PNG images.
    If single_page is provided (1-indexed), only extracts that page.
    If start_page and end_page are provided, extracts that range.
    """
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found at {pdf_path}")
        return

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"❌ Error opening PDF: {e}")
        return

    total_pages = len(doc)
    print(f"📄 Found {total_pages} pages in {pdf_path}")

    # Determine range
    if start_page is not None and end_page is not None:
        if start_page < 1 or end_page > total_pages or start_page > end_page:
            print(f"❌ Error: Invalid page range {start_page}-{end_page}.")
            return
        pages_to_extract = range(start_page - 1, end_page)
    elif single_page is not None:
        if single_page < 1 or single_page > total_pages:
            print(f"❌ Error: Page {single_page} is out of bounds (1-{total_pages}).")
            return
        pages_to_extract = [single_page - 1]
    else:
        pages_to_extract = range(total_pages)

    os.makedirs(output_dir, exist_ok=True)

    for page_idx in pages_to_extract:
        page_num = page_idx + 1
        page = doc[page_idx]
        
        # Using a zoom factor to get higher resolution images
        zoom = 2.0  # 2x zoom is usually good for OCR
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        output_filename = os.path.join(output_dir, f"page-{page_num:03d}.png")
        pix.save(output_filename)
        print(f"✅ Extracted: {output_filename}")

    doc.close()
    print("🎉 Extraction complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract PDF pages to PNG.")
    parser.add_argument("pdf_path", help="Path to the source PDF file")
    parser.add_argument("--page", type=int, help="Single page number to extract (1-indexed)")
    parser.add_argument("--start", type=int, help="Start page number (1-indexed)")
    parser.add_argument("--end", type=int, help="End page number (inclusive, 1-indexed)")
    parser.add_argument("--out", default=".", help="Output directory for images")
    
    args = parser.parse_args()
    extract_pages_to_images(args.pdf_path, args.out, args.page, args.start, args.end)
