import os
import json
import time
import google.generativeai as genai
from google.api_core import exceptions

# ============================================================================
#  FREE-TIER MODEL FALLBACK CHAIN (SAFE)
#  We try these in order. The first one that works wins.
# ============================================================================
MODEL_CHAIN = [
    "gemini-2.0-flash",       # Newest/Best if available
    "gemini-1.5-flash",       # Current Standard
    "gemini-1.5-flash-latest",# Latest alias
    "gemini-1.5-flash-001",   # Stable version
    "gemini-1.5-pro"          # Fallback to Pro if Flash fails
]

# 1. Setup
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=API_KEY)

def get_working_model():
    """Iterates through MODEL_CHAIN to find a usable model."""
    print("🔄 Finding the best available model...")
    
    for model_name in MODEL_CHAIN:
        try:
            print(f"   Testing: {model_name}...", end=" ")
            model = genai.GenerativeModel(model_name)
            # Simple test generation to verify access
            model.generate_content("Hello") 
            print("✅ Success!")
            return model_name
        except Exception as e:
            # Catch 404s, 403s, or "not found" errors
            print(f"❌ Failed.")
            continue
            
    raise ValueError(f"All models in the chain failed. Checked: {MODEL_CHAIN}")

# Initialize the working model once
ACTIVE_MODEL_NAME = get_working_model()

def translate_chapter(pdf_file, chapter):
    # Use the model we validated above
    model = genai.GenerativeModel(model_name=ACTIVE_MODEL_NAME)

    prompt = f"""
    Analyze pages {chapter['start_page']} to {chapter['end_page']} of the provided PDF.
    This is chapter: {chapter['topic']}.

    **TASK 1: TRANSLATION (Story/Poem)**
    Extract the main story or poem content.
    - Ignore headers, footers, and page numbers.
    - Output a Markdown table with columns: | Telugu | Pronunciation | Meaning |
    - Ensure Pronunciation uses simple English phonetics.

    **TASK 2: SEPARATOR**
    Output strictly this string on a new line: <<<SPLIT_HERE>>>

    **TASK 3: EXERCISES**
    Solve the exercises found in these pages.
    Format each question block exactly like this:
    #### Q: [Telugu Question Text]
    * **Pronunciation:** [English Script]
    * **Meaning:** [English Translation]
    * **Answer:** [Telugu Answer]
    """

    # Retry logic for the actual content generation
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content([pdf_file, prompt])
            return response.text
        except exceptions.ResourceExhausted:
            wait_time = (attempt + 1) * 10
            print(f"   ⚠️ Quota hit. Sleeping {wait_time}s...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"   ⚠️ Error generating content: {e}")
            if attempt == max_retries - 1:
                raise e
            time.sleep(2)

def main():
    # Load Config
    config_path = 'class5/chapters.json'
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")

    with open(config_path, 'r') as f:
        config = json.load(f)

    # Upload PDF
    print(f"📂 Uploading PDF: {config['pdf_path']}...")
    try:
        pdf_file = genai.upload_file(path=config['pdf_path'])
    except Exception as e:
        print(f"❌ Error uploading PDF. Check if path exists in repo.")
        raise e
    
    # Wait for processing
    print("⏳ Waiting for PDF processing...")
    while pdf_file.state.name == "PROCESSING":
        time.sleep(2)
        pdf_file = genai.get_file(pdf_file.name)
    
    if pdf_file.state.name == "FAILED":
        raise ValueError("PDF processing failed by Google API.")

    print(f"🚀 Starting translation using model: {ACTIVE_MODEL_NAME}")

    # Process Chapters
    for chapter in config['chapters']:
        print(f"   translating {chapter['folder']}...", end=" ")
        
        try:
            full_response = translate_chapter(pdf_file, chapter)
            
            if not full_response:
                print("❌ Empty response.")
                continue

            # Parsing the output
            if "<<<SPLIT_HERE>>>" in full_response:
                translation_part, exercise_part = full_response.split("<<<SPLIT_HERE>>>")
            else:
                translation_part = full_response
                exercise_part = "Exercises could not be parsed automatically. Please check logs."

            # Define paths
            base_path = f"class5/{chapter['folder']}"
            os.makedirs(base_path, exist_ok=True)

            # Write Translation MD
            with open(f"{base_path}/translation.md", "w", encoding="utf-8") as f:
                f.write(f"# 📖 {chapter['topic']}\n\n")
                f.write(translation_part.strip())

            # Write Exercise MD
            with open(f"{base_path}/exercise.md", "w", encoding="utf-8") as f:
                f.write(f"# ✍️ {chapter['topic']} - Exercises\n\n")
                f.write(exercise_part.strip())
                
            print(f"✅ Done.")
            
            # Sleep to be kind to free tier limits
            time.sleep(5) 

        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
