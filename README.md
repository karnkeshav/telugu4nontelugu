# Telugu Buddy

An Android app that helps children who don't speak Telugu at home learn it through their school syllabus. Content follows the Telangana state textbooks (OM editions), Classes 5 through 8.

The entire UI is HTML/CSS/JavaScript served from inside the APK via a WebView. The Android shell is minimal — it loads one file and handles the back button. All learning content, TTS, and styling lives in the web layer.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Content Pipelines](#content-pipelines)
  - [Pipeline A — AI-Powered (Class 5)](#pipeline-a--ai-powered-class-5)
  - [Pipeline B — Direct HTML (Class 6 & 8)](#pipeline-b--direct-html-class-6--8)
- [GitHub Actions Workflows](#github-actions-workflows)
- [Python Scripts](#python-scripts)
- [lesson-shared.js — The Shared Engine](#lesson-sharedjs--the-shared-engine)
- [Text-to-Speech System](#text-to-speech-system)
- [chapters.json — Content Config](#chaptersjson--content-config)
- [Android App](#android-app)
- [Building the APK](#building-the-apk)
- [Secrets & Environment Variables](#secrets--environment-variables)
- [Adding New Content](#adding-new-content)
- [Active Content](#active-content)

---

## How It Works

```
PDF textbook
     │
     ├─► Pipeline A (Class 5)
     │      Gemini AI ──► Markdown files ──► GitHub Actions ──► lesson.html / exercise.html
     │
     └─► Pipeline B (Class 6, 8)
            Hand-crafted / AI-assisted HTML written directly
            
Both pipelines produce:
    app/src/main/assets/class<N>/<NN_Chapter>/lesson.html
    app/src/main/assets/class<N>/<NN_Chapter>/exercise.html

Android WebView loads:
    file:///android_asset/index.html
    → class<N>/index.html
    → chapter/lesson.html  or  chapter/exercise.html
```

Every lesson/exercise page pulls one shared script (`lesson-shared.js`) that injects fonts, CSS, and the TTS engine. No CSS framework, no build step required for the web layer.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Android shell | Kotlin, WebView, AppCompat |
| Build system | Gradle (Kotlin DSL) |
| UI layer | Vanilla HTML5 / CSS3 / JavaScript |
| Telugu font | Noto Sans Telugu via Google Fonts |
| TTS Tier 1 | Web Speech API (`te-IN` voice) |
| TTS Tier 2 | Sound of Text API (Google Cloud TTS proxy) |
| Content AI | Google Gemini API (`gemini-2.0-flash`, model-chain fallback) |
| OCR | Tesseract 5 with `tel` language pack |
| PDF extraction | PyMuPDF (`fitz`), pdfplumber, pypdf |
| Automation | GitHub Actions (6 workflows) |
| Python scripts | 3.10 / 3.11 |

---

## Repository Structure

```
telugu4nontelugu/
│
├── app/                                  ← Android project
│   ├── build.gradle.kts
│   ├── proguard-rules.pro
│   └── src/main/
│       ├── java/com/telugu4nontelugu/    ← Kotlin source (MainActivity)
│       └── assets/                       ← WebView content root (bundled in APK)
│           ├── index.html                ← Home screen (class selector)
│           ├── style.css                 ← Home screen styles
│           ├── class5/
│           │   ├── index.html
│           │   ├── 01_Pandem/
│           │   │   ├── lesson.html
│           │   │   └── exercise.html
│           │   └── ... (10 chapters)
│           ├── class6/
│           │   ├── index.html
│           │   ├── lesson-shared.js      ← shared font + CSS + TTS
│           │   └── ... (10 chapters)
│           └── class8/
│               ├── index.html
│               ├── lesson-shared.js
│               └── ... (8 chapters)
│
├── class5/                               ← Source/working files (NOT bundled)
│   ├── pdf/5th telugu om 2025-26.pdf
│   ├── chapters.json                     ← chapter config for automation
│   └── 01_Pandem/
│       ├── lesson_1.md                   ← AI-generated translation
│       ├── exercise_1.md                 ← AI-generated exercises
│       ├── translation.md
│       └── exercise.pdf                  ← sliced from source PDF
│
├── class6/                               ← Source/working files (NOT bundled)
│   ├── pdf/6th Tel for OM 2025-26.pdf
│   ├── chapters.json
│   ├── lesson-shared.js
│   └── 01_Illu/
│       ├── lesson_1.md
│       ├── exercise_1.md
│       └── images/
│
├── .github/workflows/                    ← GitHub Actions (6 workflows)
│   ├── generate_structure.yml
│   ├── auto_translate.yml
│   ├── process_lesson.yml
│   ├── process_exercises.yml
│   ├── ocr_automation.yml
│   └── slice_pdf.yml
│
├── scripts/                              ← Python helper scripts
│   ├── translate_chapters.py             ← Gemini AI translation
│   ├── build_html.py                     ← MD → HTML via templates
│   ├── process_scanned_chapters.py       ← Tesseract OCR pipeline
│   ├── extract_pdf_images.py
│   ├── organize_ocr_content.py
│   └── translate_chapters.py
│
├── templates/                            ← HTML page templates
│   ├── lesson_template.html
│   ├── exercise_template.html
│   ├── chapter_template.html
│   └── index_template.html
│
├── docs/                                 ← GitHub Pages output (generated)
├── scanned_images/                       ← Processed PNG pages (archived here)
├── agents.md                             ← Gemini agent build instructions
├── PRODUCT_MANUAL.md                     ← Full product manual
├── build.gradle.kts
└── settings.gradle.kts
```

> **Important:** `class5/` and `class6/` at the repo root are **working directories** — they hold PDFs, markdown drafts, and OCR output. They are not served to the app. Only `app/src/main/assets/` is bundled into the APK.

---

## Content Pipelines

There are two distinct pipelines depending on the class. Both end up producing `lesson.html` and `exercise.html` files that land in `app/src/main/assets/`.

### Pipeline A — AI-Powered (Class 5)

Used for Class 5 where the PDF is machine-readable. The pipeline is fully automatable via GitHub Actions.

```
[1] Source PDF
    class5/pdf/5th telugu om 2025-26.pdf

[2] chapters.json defines chapter boundaries
    { "folder": "01_Pandem", "start_page": 12, "end_page": 22, "topic": "..." }

[3] auto_translate.yml  →  scripts/translate_chapters.py
    Uploads PDF to Gemini Files API
    Prompts: word-by-word translation table + all exercise Q&A
    Outputs:
        class5/01_Pandem/translation.md   ← Telugu | Pronunciation | Meaning table
        class5/01_Pandem/exercise.md      ← Q1, Q2 … with answers

[4] process_lesson.yml  (per-chapter, manual trigger)
    Reads lesson_N.md → prompts Gemini → outputs lesson.html
    Wraps each sentence in a card with per-word table

[5] process_exercises.yml  (per-chapter, manual trigger)
    Reads exercise_N.md + lesson_N.md context → prompts Gemini → outputs exercise.html
    Produces Bootstrap Q&A card HTML

[6] slice_pdf.yml  (optional)
    Extracts specific pages from source PDF → exercise.pdf (for reference)

[7] Resulting HTML files manually reviewed and moved to:
    app/src/main/assets/class5/<chapter>/lesson.html
    app/src/main/assets/class5/<chapter>/exercise.html
```

**Gemini model chain** (tries each in order, falls back on quota/error):
1. `gemini-2.0-flash`
2. `gemini-1.5-flash`
3. `gemini-1.5-flash-latest`
4. `gemini-1.5-pro`

### Pipeline B — Direct HTML (Class 6 & 8)

Used when the source PDF has custom font encoding that makes AI extraction unreliable. Content is written directly as HTML using a fixed template.

```
[1] Source PDF
    Structural info extracted with pdfplumber / pypdf (bookmarks, page ranges)
    Text may be partially garbled (CID font encoding) — used for structure only

[2] OCR fallback (optional)
    ocr_automation.yml  →  scripts/process_scanned_chapters.py
    Scanned page PNGs uploaded to repo root (page-067.png …)
    Tesseract (tel) extracts verbatim Telugu text
    Outputs: class6/<chapter>/lesson_N.md  and  exercise_N.md
    Processed images moved to scanned_images/

[3] HTML written directly following a fixed template
    Every file loads: <script src="../lesson-shared.js"></script>
    lesson.html  — 4-column table: Telugu | Pronunciation | Meaning | 🔊
    exercise.html — 6 qa-block divs per chapter

[4] Files committed directly to:
    app/src/main/assets/class6/<chapter>/lesson.html
    app/src/main/assets/class8/<chapter>/lesson.html
```

The `lesson-shared.js` file eliminates the need for inline CSS — all styling, the Telugu font, and the TTS engine are injected by the script at parse time.

---

## GitHub Actions Workflows

All workflows are under `.github/workflows/`. Five of six are manually triggered (`workflow_dispatch`); one auto-triggers on image uploads.

### 1. `generate_structure.yml` — Scaffold Class Content

**Trigger:** Manual, via GitHub Actions UI  
**Inputs:**
- `class_folder_name` — e.g. `class5`
- `chapter_list` — comma-separated chapter names

**What it does:**
- Creates `<class>/<NN_ChapterName>/` directories for every chapter
- Generates stub `translation.md` and `exercise.md` with placeholder tables
- Creates `<class>/README.md` as a table of contents with links
- Commits and pushes to the current branch

**Use this when:** Setting up a brand new class from scratch before any content is available.

---

### 2. `auto_translate.yml` — AI Translation via Gemini

**Trigger:** Manual  
**Secret required:** `GEMINI_API_KEY`

**What it does:**
- Runs `scripts/translate_chapters.py`
- Reads `class5/chapters.json` for chapter page ranges
- Uploads the source PDF to Gemini Files API
- Prompts Gemini for a word-by-word translation table AND all exercise Q&A
- Writes `translation.md` and `exercise.md` per chapter
- Commits and pushes changes

**Retry logic:** 3 attempts per chapter; waits 20 s on quota (HTTP 429) errors.

---

### 3. `process_lesson.yml` — Generate lesson.html from Markdown

**Trigger:** Manual  
**Input:** `chapter_folder` (dropdown of Class 5 chapters)  
**Secret required:** `GEMINI_API_KEY`

**What it does:**
- Reads `class5/<chapter>/lesson_N.md`
- Sends it to Gemini with a prompt to produce sentence cards with per-word tables
- Wraps the output in a full HTML page with Bootstrap 5 and mobile-safe CSS
- Writes `class5/<chapter>/lesson.html`
- Commits and pushes

**Output format:** Each sentence becomes a card. Inside, a `table-layout: fixed` table breaks down every word (Telugu | Pronunciation | Meaning).

---

### 4. `process_exercises.yml` — Generate exercise.html from Markdown

**Trigger:** Manual  
**Input:** `chapter_folder` (dropdown of Class 5 chapters)  
**Secret required:** `GEMINI_API_KEY`

**What it does:**
- Reads `class5/<chapter>/exercise_N.md` (questions) + `lesson_N.md` (context)
- Prompts Gemini to produce Q&A card HTML with Telugu pronunciation and meaning on both Q and A
- Handles question types: direct Q&A, fill-in-the-blank, match-the-following
- Wraps output in Bootstrap 5 page
- Writes `class5/<chapter>/exercise.html`
- Commits and pushes

**Model chain:** `gemini-2.0-flash` → `gemini-1.5-flash` → `gemini-1.5-flash-latest` → `gemini-1.5-pro`; sleeps 30 s on rate limit before trying next model.

---

### 5. `ocr_automation.yml` — Tesseract OCR on Scanned Images

**Trigger:** Manual **or** auto on push of `page-*.png` files  
**No secrets required**

**What it does:**
- Installs Tesseract with the `tesseract-ocr-tel` language pack
- Runs `scripts/process_scanned_chapters.py`
- Reads `page-NNN.png` images from repo root
- Performs OCR with `lang=tel` (Telugu)
- Assigns pages to chapters based on `CHAPTER_MAPPING` in the script
- Writes `lesson_N.md` and `exercise_N.md` per chapter to `class6/<chapter>/`
- Moves processed images to `scanned_images/`
- Commits and pushes

**Use this when:** The source PDF cannot be read by AI (garbled CID encoding). Upload page PNGs to the repo root and trigger this workflow.

---

### 6. `slice_pdf.yml` — Extract Pages from Source PDF

**Trigger:** Manual  
**Inputs:**
- `chapter_folder` — which chapter to target
- `page_numbers` — range like `5-8` or single page `12`

**What it does:**
- Uses PyMuPDF (`fitz`) to extract the specified page range from `class5/pdf/*.pdf`
- Saves the result as `class5/<chapter>/exercise.pdf`
- Commits and pushes

**Use this when:** You want a reference PDF of just the exercise pages for a chapter (useful for review or offline reference).

---

## Python Scripts

### `scripts/translate_chapters.py`

Full AI translation pipeline. Can be run locally or via `auto_translate.yml`.

```bash
export GEMINI_API_KEY=your_key

# Translate all chapters
python scripts/translate_chapters.py

# Translate one chapter
python scripts/translate_chapters.py 01_Pandem
```

Key functions:
- `list_and_find_working_model()` — queries the Gemini API for available models, tests each with a ping, returns the first working one
- `get_translation()` — generates the word-by-word markdown table
- `get_exercises()` — extracts all questions with pronunciation, meaning, and answers
- Uploads PDF once, reuses the `pdf_file` handle across all chapters, deletes it on completion

---

### `scripts/build_html.py`

Converts markdown source files to HTML using templates. Writes to `docs/` for GitHub Pages.

```bash
pip install markdown2
python scripts/build_html.py
```

- Reads `chapters.json` for each class (skips `class5` — it has a hand-crafted golden set)
- Converts `translation.md` → `lesson.html` and `exercise.md` → `exercise.html`
- Uses `templates/lesson_template.html`, `templates/exercise_template.html`
- Respects `"enabled": false` in `chapters.json` to skip incomplete chapters
- Copies `style.css` to `docs/`

---

### `scripts/process_scanned_chapters.py`

OCR pipeline for scanned textbook pages.

```bash
pip install pytesseract pillow
# Also requires: sudo apt-get install tesseract-ocr tesseract-ocr-tel

python scripts/process_scanned_chapters.py
```

- Reads `page-NNN.png` from the current directory
- Assigns each page to a chapter lesson or exercise range via `CHAPTER_MAPPING`
- Calls `pytesseract.image_to_string(image, lang='tel')` per page
- Concatenates page text into `lesson_N.md` and `exercise_N.md`
- Moves all processed images to `scanned_images/`

---

### `scripts/extract_pdf_images.py`

Extracts individual pages from a PDF as PNG images (prerequisite for OCR pipeline).

---

## lesson-shared.js — The Shared Engine

Every lesson and exercise page in Class 6 and Class 8 loads this one file:

```html
<script src="../lesson-shared.js"></script>
```

It runs at parse time and injects three things into the page:

### 1. Google Font

```js
const link = document.createElement('link');
link.href = 'https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600&display=swap';
document.head.appendChild(link);
```

Noto Sans Telugu ensures correct glyph rendering for all Telugu characters. Loaded from Google CDN; cached by the browser after first use.

### 2. Full CSS

All layout, table, button, and responsive styles are injected via a `<style>` tag. No external CSS file is needed. Key rules:

| Selector | Purpose |
|----------|---------|
| `.container` | 980 px max-width white card, drop shadow |
| `.section-heading` | Orange-bordered section title |
| `table` | Vocabulary table — striped rows |
| `td:first-child` | Noto Sans Telugu font, 1.2 em, bold |
| `td:nth-child(2)` | Italic pronunciation column |
| `.speak-btn` | 38 px circular orange button |
| `.speak-btn.speaking` | Pulsing animation while audio plays |
| `.qa-block` | Exercise card with shadow |
| `.qa-header` | Orange gradient title bar |
| `.section-label` | Numbered Q badge in qa-header |
| `@media (max-width: 600px)` | Full mobile overrides (see below) |

### 3. TTS Engine

Exposes `window.speakTelugu(text, button)` globally. Called from inline `onclick` attributes:

```html
<button class="speak-btn" onclick="speakTelugu('నమస్కారం', this)">🔊</button>
```

---

## Text-to-Speech System

3-tier fallback — each tier is tried in order; failures drop silently to the next:

```
Tier 1: Web Speech API (offline)
│  window.speechSynthesis — looks for a voice with lang 'te-IN' or 'te-*'
│  Works on Android devices with Google TTS + Telugu language pack installed
│  Rate: 0.85 (slightly slower than default for learner clarity)
│
│  If no te-IN voice found → skip to Tier 2
│
Tier 2: Sound of Text API (online)
│  POST https://api.soundoftext.com/sounds
│  Body: { engine: "Google", data: { text, voice: "te" } }
│  → Returns { id }
│  Poll GET /sounds/{id} every 700 ms, up to 8 attempts
│  → Returns { status: "Done", location: "<S3-URL>" }
│  Plays audio via hidden <audio id="tts-audio"> element
│  (Uses Google Cloud TTS under the hood — no API key required)
│
│  If API fails or times out → fall to Tier 3
│
Tier 3: Silent fail
   Button shows ⚠️ for 3 seconds with tooltip "Audio unavailable — check internet"
   Resets to 🔊 automatically
```

**Button states:**

| State | Visual |
|-------|--------|
| Idle | 🔊 orange border button |
| Active | 🔊 pulsing red fill (`.speaking` class) |
| Error | ⚠️ for 3 s, then reset |

Previous speech is always cancelled before starting a new one. Only one button pulses at a time.

---

## chapters.json — Content Config

Each class that uses the automated pipeline has a `chapters.json` config at the class root.

**Class 5 format** (page-range based, drives AI translation):

```json
{
  "class_name": "Class 5",
  "pdf_path": "class5/pdf/5th telugu om 2025-26.pdf",
  "chapters": [
    {
      "folder": "01_Pandem",
      "start_page": 12,
      "end_page": 22,
      "topic": "Pandem (The Race) - A story about a rabbit and tortoise."
    }
  ]
}
```

**Class 6 format** (richer metadata, drives `build_html.py`):

```json
{
  "class_name": "Class 6",
  "pdf_path": "class6/pdf/6th Tel for OM 2025-26.pdf",
  "chapters": [
    {
      "id": 1,
      "name": "Illu",
      "telugu": "ఇల్లు",
      "enabled": true,
      "folder": "01_Illu",
      "type": "సన్నివేశ చిత్రం",
      "start_page": 2,
      "end_page": 11
    }
  ]
}
```

`"enabled": false` skips a chapter in `build_html.py` without deleting it.

---

## Android App

The Android layer is intentionally thin. Its only jobs are:

1. Host a `WebView` that loads `file:///android_asset/index.html`
2. Enable JavaScript (required for `lesson-shared.js`)
3. Enable DOM storage and local file access
4. Intercept the Android back button to navigate WebView history instead of closing the app

**Build configuration (`app/build.gradle.kts`):**

```
applicationId   com.telugu4nontelugu
minSdk          24  (Android 7.0)
targetSdk       35
compileSdk      35
versionCode     1
versionName     1.0
APK filename    Telugubuddy.apk
```

**Release build:** minification (`isMinifyEnabled = true`) and resource shrinking (`isShrinkResources = true`) are both enabled. ProGuard config in `proguard-rules.pro`.

**Dependencies:**
```
androidx.core:core-ktx:1.15.0
androidx.appcompat:appcompat:1.7.0
com.google.android.material:material:1.12.0
androidx.lifecycle:lifecycle-runtime-ktx:2.8.7
```

---

## Building the APK

**Prerequisites:** Android Studio (Hedgehog or later) or JDK 8+ with Gradle, Android SDK with API 35 platform installed.

```bash
# Debug build (no signing required)
./gradlew assembleDebug
# Output: app/build/outputs/apk/debug/app-debug.apk

# Release build (requires keystore configuration)
./gradlew assembleRelease
# Output: app/build/outputs/apk/release/Telugubuddy.apk
```

**Install on device via ADB:**

```bash
adb install app/build/outputs/apk/release/Telugubuddy.apk
```

**Content-only update:** Edit files under `app/src/main/assets/`, then rebuild. No Kotlin code changes are needed.

---

## Secrets & Environment Variables

| Secret | Where set | Used by |
|--------|-----------|---------|
| `GEMINI_API_KEY` | GitHub repo Settings → Secrets | `auto_translate.yml`, `process_lesson.yml`, `process_exercises.yml` |

To get a Gemini API key: [Google AI Studio](https://aistudio.google.com/apikey)

For local script runs, set the environment variable before executing:

```bash
# Linux / macOS
export GEMINI_API_KEY=your_api_key_here

# Windows PowerShell
$env:GEMINI_API_KEY = "your_api_key_here"
```

---

## Adding New Content

### New chapter to an existing class

1. Add an entry to `class<N>/chapters.json`
2. Create `app/src/main/assets/class<N>/NN_ChapterName/`
3. Write `lesson.html` — load `../lesson-shared.js`, use the 4-column table format
4. Write `exercise.html` — load `../lesson-shared.js`, use 6 `qa-block` divs
5. Add the chapter card to `app/src/main/assets/class<N>/index.html`

### New class

1. Create `app/src/main/assets/class<N>/` with `index.html` and a copy of `lesson-shared.js`
2. Add the class card to `app/src/main/assets/index.html` (change `onclick="return false;"` to a real `href`)
3. Add PDF to `class<N>/pdf/` and create `class<N>/chapters.json`
4. Run `generate_structure.yml` to scaffold chapter folders
5. Run `auto_translate.yml` (Pipeline A) or write HTML directly (Pipeline B)

### Responsive design rules (enforced by lesson-shared.js)

- All pages must have: `<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">`
- Tables: `table-layout: fixed` kicks in at ≤ 600 px; all cells use `word-break: break-word`
- Column widths at mobile: Telugu 22%, Pronunciation 25%, Meaning 41%, Speak 12%
- Chapter index cards: stack vertically (`flex-direction: column`) on mobile

---

## Active Content

| Class | Book | Chapters | Status |
|-------|------|----------|--------|
| Class 5 | Tenepalukulu 5 | 10 | Active |
| Class 6 | Nawa Vasantam 1 | 10 | Active |
| Class 7 | Nawa Vasantam 2 | — | Coming Soon |
| Class 8 | Nawa Vasantam 3 | 8 | Active |
| Classes 1–4 | Jabili 1–4 | — | Coming Soon |
