import os
import json
import time
import argparse
from google import genai
from google.api_core import exceptions

# 1. Setup & Key Verification
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("❌ CRITICAL: GEMINI_API_KEY is missing from environment variables!")
    exit(1)


def list_and_find_working_model(client: genai.client.Client):
    """Lists available models and finds a usable one."""
    print("🔄 Listing available models...")
    available_models = []
    for m in client.models.list():
        # Corrected attribute name based on debugging output
        if "generateContent" in m.supported_actions:
            available_models.append(m.name)
            print(f"  - Found model supporting generateContent: {m.name}")

    if not available_models:
        print("🔥 FATAL: No models supporting 'generateContent' found.")
        exit(1)

    print("\n🔄 Testing model connectivity...")
    flash_models = [m for m in available_models if "flash" in m]
    other_models = [m for m in available_models if "flash" not in m]
    models_to_test = flash_models + other_models

    for model_name in models_to_test:
        try:
            print(f"   👉 Attempting: {model_name}...", end=" ")
            response = client.models.generate_content(model=model_name, contents=["Hi"])
            if response.text:
                print("✅ SUCCESS!")
                return model_name
            else:
                print("\n      ⚠️ Received empty response.")
        except Exception as e:
            print(f"\n      ❌ FAILED. Error details: {str(e)}")
            continue
            
    print("🔥 FATAL: All tested models failed.")
    exit(1)


def get_translation(client: genai.client.Client, model_name: str, pdf_file, chapter):
    prompt = f"""
    You are a meticulous educational translator for a Class 5 Telugu textbook. Your task is to be 100% accurate and complete.
    Analyze pages {chapter['start_page']} to {chapter['end_page']} of the provided PDF.
    Topic: {chapter['topic']}.

    **TASK: TRANSLATION (Story/Poem)**
    - You MUST provide a complete, word-by-word translation of the story or poem.
    - You MUST process every single line of the text from the specified pages. Do not skip any content.
    - Output a single Markdown table with three columns: | Telugu | Pronunciation | Meaning |.
    - The process for each sentence is as follows:
    1.  First, create a row for the complete sentence. The text in all three columns for this row must be bold (e.g., `**Full Sentence**`).
    2.  Then, for each individual word in that sentence, create a new row in the table.
    - This structure is mandatory.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=model_name, contents=[pdf_file, prompt])
            return response.text
        except exceptions.ResourceExhausted:
            print(f"   ⚠️ Quota hit. Sleeping 20s...")
            time.sleep(20)
        except Exception as e:
            print(f"   ⚠️ Error during translation generation: {e}")
            if attempt == max_retries - 1:
                raise e
            time.sleep(5)


def get_exercises(client: genai.client.Client, model_name: str, pdf_file, chapter):
    prompt = f"""
    You are a meticulous educational translator for a Class 5 Telugu textbook. Your task is to be 100% accurate and complete.

    **TASK: EXERCISES**
    - You MUST identify and process EVERY exercise, question, and grammar task ONLY from pages {chapter['start_page']} to {chapter['end_page']} of the provided PDF. Do not include exercises from any other pages. This includes questions based on images, which you must analyze and answer.
    - You MUST number each question sequentially, starting from Q1. The format must be `#### Q1: [Telugu Text]`, `#### Q2: [Telugu Text]`, etc.
    - For EVERY question, you MUST provide all four of the following fields. NO field can be left blank. If a field is not applicable, write 'Not Applicable', but do not leave it empty.
        * **Pronunciation:** [Simple English Pronunciation]
        * **Meaning:** [English Meaning]
        * **Answer:** [Telugu Answer]
        * **Answer Pronunciation:** [Simple English Pronunciation of Answer]
    - For questions with multiple parts or sub-answers (e.g., fill-in-the-blanks, matching), list all parts clearly under the single question number.
    - Maintain the exact formatting provided below. Do not deviate.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=model_name, contents=[pdf_file, prompt])
            return response.text
        except exceptions.ResourceExhausted:
            print(f"   ⚠️ Quota hit. Sleeping 20s...")
            time.sleep(20)
        except Exception as e:
            print(f"   ⚠️ Error during exercise generation: {e}")
            if attempt == max_retries - 1:
                raise e
            time.sleep(5)


def main():
    parser = argparse.ArgumentParser(description="Translate chapters from a PDF.")
    parser.add_argument(
        "chapter_folder",
        nargs="?",
        default=None,
        help="The specific chapter folder to process (e.g., '01_Pandem'). If not provided, all chapters will be processed.",
    )
    args = parser.parse_args()

    client = genai.Client()
    active_model_name = list_and_find_working_model(client)
    print(f"🚀 Using model: {active_model_name}")

    config_path = "class5/chapters.json"
    if not os.path.exists(config_path):
        print(f"❌ Config not found at: {config_path}")
        exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    print(f"📂 Uploading PDF: {config['pdf_path']}...")
    try:
        pdf_file = client.files.upload(file=config["pdf_path"])
    except Exception as e:
        print(f"❌ Upload Failed. Check file path. Details: {e}")
        exit(1)

    print("⏳ Waiting for PDF processing...")
    while pdf_file.state.name == "PROCESSING":
        time.sleep(10)
        pdf_file = client.files.get(name=pdf_file.name)

    if pdf_file.state.name == "FAILED":
        print("❌ PDF processing failed by Google API.")
        try:
            client.files.delete(name=pdf_file.name)
        except Exception as e:
            print(f"   Could not delete failed file: {e}")
        exit(1)

    print("✅ PDF processed successfully.")

    chapters_to_process = []
    if args.chapter_folder:
        chapter_to_process = next(
            (ch for ch in config["chapters"] if ch["folder"] == args.chapter_folder), None
        )
        if chapter_to_process:
            chapters_to_process.append(chapter_to_process)
        else:
            print(f"❌ Chapter folder '{args.chapter_folder}' not found in {config_path}")
            exit(1)
    else:
        chapters_to_process = config["chapters"]

    for chapter in chapters_to_process:
        print(f"   Translating {chapter['folder']}...")
        try:
            print("      - Generating translation...", end=" ")
            trans = get_translation(client, active_model_name, pdf_file, chapter)
            if not trans:
                print("❌ Empty response.")
                trans = "Translation failed."
            else:
                print("✅")

            print("      - Generating exercises...", end=" ")
            exer = get_exercises(client, active_model_name, pdf_file, chapter)
            if not exer:
                print("❌ Empty response.")
                exer = "Exercises parse failed. Check raw output."
            else:
                print("✅")

            base_path = f"class5/{chapter['folder']}"
            os.makedirs(base_path, exist_ok=True)
            with open(f"{base_path}/translation.md", "w", encoding="utf-8") as f:
                f.write(f"# 📖 {chapter['topic']}\n\n{trans.strip()}")
            with open(f"{base_path}/exercise.md", "w", encoding="utf-8") as f:
                f.write(f"# ✍️ Exercises\n\n{exer.strip()}")
            print(f"   ✅ Done with {chapter['folder']}.")
            time.sleep(5)
        except Exception as e:
            print(f"❌ Error processing {chapter['folder']}: {e}")

    try:
        client.files.delete(name=pdf_file.name)
        print(f"✅ Cleaned up uploaded file: {pdf_file.display_name}")
    except Exception as e:
        print(f"   ⚠️ Could not delete uploaded file: {e}")


if __name__ == "__main__":
    main()
