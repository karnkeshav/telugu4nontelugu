import os
import shutil
import re
import pytesseract
from PIL import Image

# --- CONFIGURATION ---
SOURCE_DIR = "."                # Root of repo where images are uploaded
DEST_IMG_DIR = "scanned_images" # Where to store images after processing
OUTPUT_BASE = "class5"          # Base folder for chapters
OCR_LANG = "tel"                # Telugu Language Code

# Chapter Mapping based on your request and chapters.json structure
CHAPTER_MAPPING = {
    "06_Shataka_Padyalu": {
        "id": 6, 
        "lesson": (67, 70), 
        "exercise": (70, 74)
    },
    "07_Sankranthi_Sandesham": {
        "id": 7, 
        "lesson": (75, 76), 
        "exercise": (77, 80)
    },
    "08_Kanuvippu": {
        "id": 8, 
        "lesson": (81, 84), 
        "exercise": (84, 88)
    },
    "09_Ramappa": {
        "id": 9, 
        "lesson": (89, 92), 
        "exercise": (92, 96)
    },
    "10_Shibi_Chakravarti": {
        "id": 10, 
        "lesson": (97, 99), 
        "exercise": (100, 104)
    }
}

def get_ocr_text_from_root(page_num):
    """
    Searches for page-XXX.png or page-X.png in the ROOT directory.
    Returns the verbatim Telugu text found.
    """
    # Accept formats like page-067.png or page-67.png
    candidates = [f"page-{page_num:03d}.png", f"page-{page_num}.png"]
    
    img_path = None
    # Check if file exists in root
    for c in candidates:
        if os.path.exists(c):
            img_path = c
            break
            
    if not img_path:
        print(f"      ⚠️  Warning: Image for page {page_num} not found in root.")
        return f"\n\n"

    try:
        # Perform OCR using Telugu language
        text = pytesseract.image_to_string(Image.open(img_path), lang=OCR_LANG)
        return text if text.strip() else f"\n\n"
    except Exception as e:
        print(f"      ❌ OCR Error on {img_path}: {e}")
        return f"\n\n"

def cleanup_images():
    """Moves processed images from root to scanned_images folder."""
    if not os.path.exists(DEST_IMG_DIR):
        os.makedirs(DEST_IMG_DIR)
        
    print(f"\n🧹 Moving images to {DEST_IMG_DIR}...")
    
    file_pattern = re.compile(r"page-\d+\.png")
    count = 0
    
    # List files in current directory
    for filename in os.listdir(SOURCE_DIR):
        if file_pattern.match(filename) and os.path.isfile(filename):
            src = os.path.join(SOURCE_DIR, filename)
            dst = os.path.join(DEST_IMG_DIR, filename)
            try:
                shutil.move(src, dst)
                count += 1
            except Exception as e:
                print(f"   ⚠️ Could not move {filename}: {e}")
                
    print(f"✅ Moved {count} images.")

def main():
    print("🚀 Starting Verbatim OCR Processing...")

    # 1. GENERATE MARKDOWN FILES
    for folder_name, data in CHAPTER_MAPPING.items():
        chapter_id = data['id']
        print(f"\n📂 Processing Chapter {chapter_id} ({folder_name})...")
        
        # Ensure chapter folder exists (matches your repo structure)
        output_dir = os.path.join(OUTPUT_BASE, folder_name)
        os.makedirs(output_dir, exist_ok=True)

        # --- Lesson Section ---
        l_start, l_end = data['lesson']
        print(f"   📖 Generaring lesson_{chapter_id}.md (Pages {l_start}-{l_end})")
        lesson_text = ""
        for page in range(l_start, l_end + 1):
            lesson_text += get_ocr_text_from_root(page) + "\n\n"
            
        with open(os.path.join(output_dir, f"lesson_{chapter_id}.md"), "w", encoding="utf-8") as f:
            f.write(lesson_text.strip())

        # --- Exercise Section ---
        e_start, e_end = data['exercise']
        print(f"   ✍️ Generaring exercise_{chapter_id}.md (Pages {e_start}-{e_end})")
        exercise_text = ""
        for page in range(e_start, e_end + 1):
            exercise_text += get_ocr_text_from_root(page) + "\n\n"
            
        with open(os.path.join(output_dir, f"exercise_{chapter_id}.md"), "w", encoding="utf-8") as f:
            f.write(exercise_text.strip())

    # 2. CLEANUP IMAGES (Run ONLY after processing)
    cleanup_images()
    print("\n✅ All Done!")

if __name__ == "__main__":
    main()
