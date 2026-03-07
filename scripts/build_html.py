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
    # Find all classes that have a chapters.json
    class_dirs = [d for d in os.listdir(".") if d.startswith("class") and os.path.exists(os.path.join(d, "chapters.json"))]
    
    # We will aggregate all classes into a single master index or just keep the static root index
    # Currently, PR #7's index_template.html is designed for a single class.
    # To keep things simple and functional, we will generate docs/classX/index.html 
    # and rely on the root index.html to point to them. Let's process each class independently.

    # Load templates
    try:
        index_template = read_file("templates/index_template.html")
        chapter_template = read_file("templates/chapter_template.html")
        lesson_template = read_file("templates/lesson_template.html")
        exercise_template = read_file("templates/exercise_template.html")
    except FileNotFoundError as e:
        print(f"❌ Error: Template file not found - {e}. Make sure all templates exist.")
        return

    for class_dir in class_dirs:
        config_path = os.path.join(class_dir, "chapters.json")
        print(f"\n⚙️ Processing {class_dir} using {config_path}")
        
        # Load chapter data
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        class_name = config.get("class_name", class_dir.capitalize())
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

            chapter_output_dir = os.path.join(output_dir, class_dir, folder)

            # Paths for markdown files
            translation_md_path = os.path.join(class_dir, folder, "translation.md")
            exercise_md_path = os.path.join(class_dir, folder, "exercise.md")
            
            # For class 6, checking specifically for `lesson_` and `exercise_` files if they exist instead of `translation.md`
            if not os.path.exists(translation_md_path):
                # Fallback to lesson_X.md if translation.md doesn't exist
                lesson_files = [f for f in os.listdir(os.path.join(class_dir, folder)) if f.startswith('lesson_') and f.endswith('.md')]
                if lesson_files:
                     translation_md_path = os.path.join(class_dir, folder, lesson_files[0])
            
            if not os.path.exists(exercise_md_path):
                 # Fallback to exercise_X.md
                 exercise_files = [f for f in os.listdir(os.path.join(class_dir, folder)) if f.startswith('exercise_') and f.endswith('.md')]
                 if exercise_files:
                      exercise_md_path = os.path.join(class_dir, folder, exercise_files[0])

            if not os.path.exists(translation_md_path) or not os.path.exists(exercise_md_path):
                print(f"   ⚠️ Markdown files for {folder} not found. Skipping.")
                continue

            # Convert translation markdown to HTML
            translation_md = read_file(translation_md_path)
            translation_html = markdown2.markdown(translation_md, extras=["tables"])
            lesson_content = lesson_template.replace("{{ chapter_title }}", topic).replace("{{ content }}", translation_html)
            
            # Fix style path locally for chapter depth (e.g. docs/class5/folder/lesson.html -> ../../style.css)
            lesson_content = lesson_content.replace('href="../style.css"', 'href="../../style.css"')
            
            write_file(os.path.join(chapter_output_dir, "lesson.html"), lesson_content)

            # Convert exercise markdown to HTML
            exercise_md = read_file(exercise_md_path)
            exercise_html = markdown2.markdown(exercise_md)
            exercise_content = exercise_template.replace("{{ chapter_title }}", topic).replace("{{ content }}", exercise_html)
            exercise_content = exercise_content.replace('href="../style.css"', 'href="../../style.css"')
            write_file(os.path.join(chapter_output_dir, "exercise.html"), exercise_content)

            # Create chapter index page
            chapter_index_content = chapter_template.replace("{{ chapter_title }}", topic)
            chapter_index_content = chapter_index_content.replace('href="../style.css"', 'href="../../style.css"')
            write_file(os.path.join(chapter_output_dir, "index.html"), chapter_index_content)

            # Add link to class index
            chapter_links.append(f'<li><a href="{folder}/index.html">{topic}</a></li>')

        # Create class index page
        class_index_content = index_template.replace("{{ class_name }}", class_name).replace("{{ chapter_links }}", "\n".join(chapter_links))
        class_index_content = class_index_content.replace('href="../style.css"', 'href="../style.css"')
        write_file(os.path.join(output_dir, class_dir, "index.html"), class_index_content)

    # Copy stylesheet to docs root
    style_content = read_file("style.css")
    write_file(os.path.join(output_dir, "style.css"), style_content)

    print("✅ Build complete! Website generated in 'docs' directory.")

if __name__ == "__main__":
    main()
