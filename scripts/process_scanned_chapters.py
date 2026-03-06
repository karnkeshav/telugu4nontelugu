import os
import shutil
import re
import pytesseract
from PIL import Image

# --- CONFIGURATION ---
SOURCE_DIR = "."                # Root of repo where images are uploaded
DEST_IMG_DIR = "scanned_images" # Where to store images after processing
OUTPUT_BASE = "class6"          # UPDATED FOR CLASS 6
OCR_LANG = "tel"                # Telugu Language Code

# Chapter Mapping for Class 6
CHAPTER_MAPPING = {
    "01_Amma_Odi": {"id": 1, "lesson": (1, 6), "exercise": (7, 12)},
    "02_Trupti": {"id": 2, "lesson": (13, 18), "exercise": (19, 24)},
    "03_Maakoddi_Tella_Doratanamu": {"id": 3, "lesson": (25, 30), "exercise": (31, 36)},
    "04_Samayaspurthi": {"id": 4, "lesson": (37, 42), "exercise": (43, 48)},
    "05_Mana_Mahaneeyulu": {"id": 5, "lesson": (49, 54), "exercise": (55, 60)},
    "06_Subhashitalu": {"id": 6, "lesson": (61, 66), "exercise": (67, 72)},
    "07_Mamakaram": {"id": 7, "lesson": (73, 78), "exercise": (79, 84)},
    "08_Melukolupu": {"id": 8, "lesson": (85, 90), "exercise": (91, 96)},
    "09_Dharma_Nirnayam": {"id": 9, "lesson": (97, 102), "exercise": (103, 108)},
    "10_Du_Du_Basavanna": {"id": 10, "lesson": (109, 114), "exercise": (115, 120)},
    "11_Entha_Manchivaaramma": {"id": 11, "lesson": (121, 126), "exercise": (127, 132)}
}

def get_ocr_text_from_root(page_num):
    """
    Searches for page-XXX.png or page-X.png in the ROOT directory.
    Returns the verbatim Telugu text found.
    """
    candidates = [f"page-{page_num:03d}.png", f"page-{page_num}.png"]
    img_path = None
    for c in candidates:
        if os.path.exists(c):
            img_path = c
            break
            
    if not img_path:
        return f"\n\n"

    try:
        text = pytesseract.image_to_string(Image.open(img_path), lang=OCR_LANG)
        return text if text.strip() else f"\n\n"
    except Exception as e:
        return f"\n\n"

def cleanup_images():
    """Moves processed images from root to scanned_images folder."""
    if not os.path.exists(DEST_IMG_DIR):
        os.makedirs(DEST_IMG_DIR)
    
    file_pattern = re.compile(r"page-\d+\.png")
    for filename in os.listdir(SOURCE_DIR):
        if file_pattern.match(filename) and os.path.isfile(filename):
            src = os.path.join(SOURCE_DIR, filename)
            dst = os.path.join(DEST_IMG_DIR, filename)
            try:
                shutil.move(src, dst)
            except Exception:
                pass

def main():
    print(f"🚀 Starting Verbatim OCR Processing for {OUTPUT_BASE}...")

    for folder_name, data in CHAPTER_MAPPING.items():
        chapter_id = data['id']
        output_dir = os.path.join(OUTPUT_BASE, folder_name)
        os.makedirs(output_dir, exist_ok=True)

        # --- Lesson Section ---
        l_start, l_end = data['lesson']
        lesson_text = ""
        for page in range(l_start, l_end + 1):
            lesson_text += get_ocr_text_from_root(page) + "\n\n"
            
        with open(os.path.join(output_dir, f"lesson_{chapter_id}.md"), "w", encoding="utf-8") as f:
            f.write(lesson_text.strip())

        # --- Exercise Section ---
        e_start, e_end = data['exercise']
        exercise_text = ""
        for page in range(e_start, e_end + 1):
            exercise_text += get_ocr_text_from_root(page) + "\n\n"
            
        with open(os.path.join(output_dir, f"exercise_{chapter_id}.md"), "w", encoding="utf-8") as f:
            f.write(exercise_text.strip())

    cleanup_images()
    print("\n✅ All Done!")

if __name__ == "__main__":
    main()