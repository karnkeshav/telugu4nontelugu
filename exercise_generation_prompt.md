# Standard Prompt for Generating Chapter Exercises

This is the standard, strict, comprehensive master prompt to generate the `exercise.html` for any chapter identically to Chapter 1 and Chapter 3, guaranteeing zero data loss and exact 1:1 format replication.

Copy and paste the below request whenever you need to generate a new chapter's exercise:

---

### Master Prompt:

**Objective:**
Create the `exercise.html` file for Class 6 Chapter `[X]`. The goal is to transcribe **100%** of the exercise content from the scanned images in the `class6/[Chapter_Name]/images/` directory.

**Source Material:**
1. Reference the format, HTML structure, and CSS styling exactly from `class6/01_Illu/exercise.html`.
2. Review the lesson text in `class6/[Chapter_Name]/images/` to know the context, and then transcribe **all the exercise pages** word-by-word, line-by-line, and page-by-page. Do NOT skip any section, sub-section, question, matching exercise, fill-in-the-blank, or table.

**Strict Generation Rules:**
1. **No Summarization or Truncation:** You must transcribe every single word of the exercise. Do not summarize, skip, or group questions together. If there is a table with 12 items, transcribe all 12 items.
2. **Four-Part Data Requirement for EVERY Telugu word/phrase:**
   For every piece of Telugu text (Headers, Questions, Answers, Options, Grid words), you MUST provide:
   - The original **Telugu text**.
   - The **English Phonetic Pronunciation** (in brackets, italicized where appropriate).
   - The **English Meaning/Translation**.
   - A functioning **🔊 Speaker Button** using the `speakTelugu('text', this)` function.
3. **Structure & Layout:**
   - Use the established HTML classes: `.qa-block`, `.qa-header`, `.section-label`, `.telugu-text`, `.english-text`, `.activity-box`, and `.ans-table`.
   - Separate major Roman Numeral sections (e.g., I, II, III) with horizontal comments and `.sub-header` tags.
   - For matching pairs, tables, and fill-in-the-blanks, use the `.ans-table` structure with clear columns for the Answer, Pronunciation/Meaning, and Audio button.
4. **Answering Questions:**
   - If the exercise asks questions based on the lesson, **you must synthesize and provide the correct answer in Telugu.**
   - Include the pronunciation, meaning, and audio button for your supplied answers as well.
5. **Token Limit Management (CRITICAL):**
   - Because these exercise files contain hundreds of words/buttons and are very large, **DO NOT attempt to output the entire file in one response.**
   - First, write the base HTML skeleton with placeholders (`<!-- PART1_START -->...`).
   - Then, use iterative `multi_replace_file_content` tool calls to inject each section (Chunk 1, Chunk 2, etc.) one by one until the full file is completely built. Do not stop until every page of the exercise is transcribed.

**Deliverable:**
A single, complete, fully-functional `exercise.html` in the target chapter directory that perfectly mirrors the textbook exercises with added English translations, pronunciations, and audio buttons for non-native learners.
---
