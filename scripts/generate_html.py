import os
import re

def generate_lesson_page(chapter_title, md_content, template):
    table_rows = []
    lines = md_content.strip().splitlines()

    # Find the table header separator
    try:
        separator_index = lines.index('|---|---|---|')
        data_lines = lines[separator_index + 1:]
    except ValueError:
        data_lines = []

    for line in data_lines:
        if line.strip() == '':
            continue
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 4:
            telugu, pronunciation, meaning = parts[1], parts[2], parts[3]
            table_rows.append(f'<tr><td>{telugu}</td><td>{pronunciation}</td><td>{meaning}</td></tr>')

    table_html = '\n'.join(table_rows)
    content = template.replace('{{CHAPTER_TITLE}}', chapter_title)
    content = content.replace('{{TABLE_ROWS}}', table_html)
    return content

def generate_exercise_page(chapter_title, md_content, template):
    exercise_cards = []

    # Find the start of the first question to ignore headers
    content_start = md_content.find('#### Q:')
    if content_start != -1:
        md_content = md_content[content_start:]

    # Split by the 'Q:' marker
    questions = md_content.split('#### Q:')
    for q_block in questions:
        if q_block.strip() == '':
            continue

        lines = q_block.strip().splitlines()
        question = lines[0]
        pronunciation = ''
        meaning = ''
        answer = ''

        for line in lines[1:]:
            if line.startswith('* **Pronunciation:**'):
                pronunciation = line.replace('* **Pronunciation:**', '').strip()
            elif line.startswith('* **Meaning:**'):
                meaning = line.replace('* **Meaning:**', '').strip()
            elif line.startswith('* **Answer:**'):
                answer = line.replace('* **Answer:**', '').strip()

        card_html = f"""
        <div class="exercise-card">
            <div class="question">Q: {question}</div>
            <div class="detail"><strong>Pronunciation:</strong> {pronunciation}</div>
            <div class="detail"><strong>Meaning:</strong> {meaning}</div>
            <div class="detail"><strong>Answer:</strong> {answer}</div>
        </div>
        """
        exercise_cards.append(card_html)

    cards_html = '\n'.join(exercise_cards)
    # The template itself adds " - Exercises", so just pass the chapter title
    content = template.replace('{{CHAPTER_TITLE}}', chapter_title)
    content = content.replace('{{EXERCISE_CARDS}}', cards_html)
    return content

def main():
    class5_dir = 'class5'
    script_dir = 'scripts'

    with open(os.path.join(script_dir, 'lesson_template.html'), 'r', encoding='utf-8') as f:
        lesson_template = f.read()

    with open(os.path.join(script_dir, 'exercise_template.html'), 'r', encoding='utf-8') as f:
        exercise_template = f.read()

    for chapter_dir in sorted(os.listdir(class5_dir)):
        chapter_path = os.path.join(class5_dir, chapter_dir)
        if os.path.isdir(chapter_path) and chapter_dir.startswith(('0', '1')):
            chapter_title = chapter_dir.split('_', 1)[1].replace('_', ' ')

            # Generate Lesson Page
            translation_md_path = os.path.join(chapter_path, 'translation.md')
            if os.path.exists(translation_md_path):
                with open(translation_md_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                lesson_html = generate_lesson_page(chapter_title, md_content, lesson_template)
                with open(os.path.join(chapter_path, 'lesson.html'), 'w', encoding='utf-8') as f:
                    f.write(lesson_html)

            # Generate Exercise Page
            exercise_md_path = os.path.join(chapter_path, 'exercise.md')
            if os.path.exists(exercise_md_path):
                with open(exercise_md_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                exercise_html = generate_exercise_page(chapter_title, md_content, exercise_template)
                with open(os.path.join(chapter_path, 'exercise.html'), 'w', encoding='utf-8') as f:
                    f.write(exercise_html)

    print("HTML generation complete.")

if __name__ == '__main__':
    main()
