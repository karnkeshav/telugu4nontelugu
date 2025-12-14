import os
import json
import time
import google.generativeai as genai
from google.api_core import exceptions

# ============================================================================
#  MODEL FALLBACK CHAIN (Updated based on your API response)
# ============================================================================
MODEL_CHAIN = [
    "gemini-2.0-flash",       # Primary: Fast & High limits
    "gemini-2.0-flash-exp",   # Secondary: Experimental version
    "gemini-flash-latest",    # Tertiary: Rolling release
    "gemini-1.5-pro-latest",  # Fallback: Higher capability
    "gemini-pro"              # Last Resort
]

# 1. Setup & Key Verification
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("❌ CRITICAL: GEMINI_API_KEY is missing from environment variables!")
    exit(1)

genai.configure(api_key=API_KEY)

def get_working_model():
    """Iterates through MODEL_CHAIN to find a usable model."""
    print("🔄 Testing model connectivity...")
    
    for model_name in MODEL_CHAIN:
        try:
            print(f"   👉 Attempting: {model_name}...", end=" ")
            model = genai.GenerativeModel(model_name)
            # Simple test generation to verify connection
            response = model.generate_content("Hi") 
            print("✅ SUCCESS!")
            return model_name
        except Exception as e:
            # We catch the error and print it so you can see if it's 404 or 403
            print(f"\n      ❌ FAILED. Error details: {str(e)}")
            continue
            
    print("🔥 FATAL: All models failed.")
    exit(1)

# Initialize the working model
ACTIVE_MODEL_NAME = get_working_model()

def translate_chapter(pdf_file, chapter):
    model = genai.GenerativeModel(model_name=ACTIVE_MODEL_NAME)

    prompt = f"""
    You are an educational translator for Class 5 students.
    Analyze pages {chapter['start_page']} to {chapter['end_page']} of the provided PDF.
    Topic: {chapter['topic']}.

    **TASK 1: TRANSLATION (Story/Poem)**
    - Ignore headers, footers, and page numbers.
    - Output a Markdown table: | Telugu | Pronunciation | Meaning |
    - Use clear English script for pronunciation.

    **TASK 2: SEPARATOR**
    Output strictly this string on a new line: <<<SPLIT_HERE>>>

    **TASK 3: EXERCISES**
    - Identify questions and grammar tasks.
    - Format exactly like this:
    #### Q: [Telugu Text]
    * **Pronunciation:** ...
    * **Meaning:** ...
    * **Answer:** [Telugu Answer]
    """

    # Retry logic for generation
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content([pdf_file, prompt])
            return response.text
        except exceptions.ResourceExhausted:
            print(f"   ⚠️ Quota hit. Sleeping 20s...")
            time.sleep(20)
        except Exception as e:
            print(f"   ⚠️ Error during generation: {e}")
            if attempt == max_retries - 1:
                raise e
            time.sleep(5)

def main():
    config_path = 'class5/chapters.json'
    if not os.path.exists(config_path):
        print(f"❌ Config not found at: {config_path}")
        exit(1)

    with open(config_path, 'r') as f:
        config = json.load(f)

    print(f"📂 Uploading PDF: {config['pdf_path']}...")
    try:
        pdf_file = genai.upload_file(path=config['pdf_path'])
    except Exception as e:
        print(f"❌ Upload Failed. Check file path. Details: {e}")
        exit(1)
    
    print("⏳ Waiting for PDF processing...")
    while pdf_file.state.name == "PROCESSING":
        time.sleep(2)
        pdf_file = genai.get_file(pdf_file.name)
    
    if pdf_file.state.name == "FAILED":
        print("❌ PDF processing failed by Google API.")
        exit(1)

    print(f"🚀 Processing with model: {ACTIVE_MODEL_NAME}")

    for chapter in config['chapters']:
        print(f"   Translating {chapter['folder']}...", end=" ")
        
        try:
            full_response = translate_chapter(pdf_file, chapter)
            
            if not full_response:
                print("❌ Empty response.")
                continue

            if "<<<SPLIT_HERE>>>" in full_response:
                trans, exer = full_response.split("<<<SPLIT_HERE>>>")
            else:
                trans = full_response
                exer = "Exercises parse failed. Check raw output."

            base_path = f"class5/{chapter['folder']}"
            os.makedirs(base_path, exist_ok=True)

            with open(f"{base_path}/translation.md", "w", encoding="utf-8") as f:
                f.write(f"# 📖 {chapter['topic']}\n\n{trans.strip()}")

            with open(f"{base_path}/exercise.md", "w", encoding="utf-8") as f:
                f.write(f"# ✍️ Exercises\n\n{exer.strip()}")
                
            print(f"✅ Done.")
            time.sleep(5) # Gentle rate limiting

        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
