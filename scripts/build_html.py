import os
import json
import markdown2

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print("🚀 Starting HTML build process...")

    # Configuration
    output_dir = "docs"
    config_path = "class5/chapters.json"

    # Load templates
    try:
        index_template = read_file("templates/index_template.html")
        chapter_template = read_file("templates/chapter_template.html")
        lesson_template = read_file("templates/lesson_template.html")
        exercise_template = read_file("templates/exercise_template.html")
    except FileNotFoundError as e:
        print(f"❌ Error: Template file not found - {e}. Make sure all templates exist.")
        return

    # Load chapter data
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    class_name = config["class_name"]
    chapter_links = []

    # Process each chapter
    for chapter in config["chapters"]:
        folder = chapter["folder"]
        topic = chapter["topic"]

        # Skip chapters that are not enabled in the config
        if not chapter.get("enabled", False):
            print(f"⏩ Skipping disabled chapter: {folder}")
            continue

        print(f"   - Processing {folder}...")

        chapter_output_dir = os.path.join(output_dir, "class5", folder)

        # Paths for markdown files
        translation_md_path = os.path.join("class5", folder, "translation.md")
        exercise_md_path = os.path.join("class5", folder, "exercise.md")

        if not os.path.exists(translation_md_path) or not os.path.exists(exercise_md_path):
            print(f"   ⚠️ Markdown files for {folder} not found. Skipping.")
            continue

        # Convert translation markdown to HTML
        translation_md = read_file(translation_md_path)
        translation_html = markdown2.markdown(translation_md, extras=["tables"])
        lesson_content = lesson_template.replace("{{ chapter_title }}", topic).replace("{{ content }}", translation_html)
        write_file(os.path.join(chapter_output_dir, "lesson.html"), lesson_content)

        # Convert exercise markdown to HTML
        exercise_md = read_file(exercise_md_path)
        exercise_html = markdown2.markdown(exercise_md)
        exercise_content = exercise_template.replace("{{ chapter_title }}", topic).replace("{{ content }}", exercise_html)
        write_file(os.path.join(chapter_output_dir, "exercise.html"), exercise_content)

        # Create chapter index page
        chapter_index_content = chapter_template.replace("{{ chapter_title }}", topic)
        write_file(os.path.join(chapter_output_dir, "index.html"), chapter_index_content)

        # Add link to main index
        chapter_links.append(f'<li><a href="class5/{folder}/index.html">{topic}</a></li>')

    # Create main index page
    main_index_content = index_template.replace("{{ class_name }}", class_name).replace("{{ chapter_links }}", "\n".join(chapter_links))
    write_file(os.path.join(output_dir, "index.html"), main_index_content)

    # Copy stylesheet
    style_content = read_file("style.css")
    write_file(os.path.join(output_dir, "style.css"), style_content)

    print("✅ Build complete! Website generated in 'docs' directory.")

if __name__ == "__main__":
    main()
