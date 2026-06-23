# Telugu Buddy — Product Manual

> **App ID:** `com.telugu4nontelugu` · **APK:** `Telugubuddy.apk` · **Version:** 1.0  
> **Minimum Android:** 7.0 (API 24) · **Target Android:** API 35

---

## Table of Contents

1. [What Is Telugu Buddy?](#1-what-is-telugu-buddy)
2. [Architecture Overview](#2-architecture-overview)
3. [Content Structure](#3-content-structure)
4. [Repository Layout](#4-repository-layout)
5. [Pages & Navigation](#5-pages--navigation)
6. [Lesson Pages (`lesson.html`)](#6-lesson-pages-lessonhtml)
7. [Exercise Pages (`exercise.html`)](#7-exercise-pages-exercisehtml)
8. [Shared Resource: `lesson-shared.js`](#8-shared-resource-lesson-sharedjs)
9. [Text-to-Speech Engine](#9-text-to-speech-engine)
10. [Responsive Design](#10-responsive-design)
11. [Available Content by Class](#11-available-content-by-class)
12. [Build & Deploy](#12-build--deploy)
13. [Adding a New Class or Chapter](#13-adding-a-new-class-or-chapter)
14. [Troubleshooting](#14-troubleshooting)

---

## 1. What Is Telugu Buddy?

Telugu Buddy is an Android application designed to help children who do not speak Telugu at home learn it as a second language. It follows the Telangana state school syllabus (OM editions) from Class 5 upward.

Each class maps to the official textbook:

| Class | Book Title | Status |
|-------|-----------|--------|
| Class 5 | Tenepalukulu 5 | Active |
| Class 6 | Nawa Vasantam 1 | Active |
| Class 7 | Nawa Vasantam 2 | Coming Soon |
| Class 8 | Nawa Vasantam 3 | Active |
| Classes 1–4 | Jabili 1–4 | Coming Soon |

For every chapter the app provides two interactive pages:

- **Lesson page** — the full vocabulary table with Telugu script, pronunciation, English meaning, and a speak button.
- **Exercise page** — comprehension Q&A blocks with answer reveal and audio support.

---

## 2. Architecture Overview

Telugu Buddy is a **WebView-first Android app**. The entire UI is built in HTML/CSS/JavaScript and bundled inside the APK under `app/src/main/assets/`. The Android layer is minimal — it hosts a `WebView` that loads `index.html` from the assets folder.

```
Android shell  (Kotlin / WebView)
       │
       └─► app/src/main/assets/   ← all user-facing content
                index.html          ← home screen
                style.css           ← home screen styles
                class5/
                class6/
                class8/
```

**Why this approach?** Content can be updated without touching Kotlin code. The entire app is a static website that happens to run inside Android.

### Android build details

| Setting | Value |
|---------|-------|
| `applicationId` | `com.telugu4nontelugu` |
| `minSdk` | 24 (Android 7.0) |
| `targetSdk` | 35 |
| `compileSdk` | 35 |
| `kotlinOptions.jvmTarget` | 1.8 |
| Release APK filename | `Telugubuddy.apk` |
| Minification (release) | enabled (`isMinifyEnabled = true`, `isShrinkResources = true`) |

---

## 3. Content Structure

Each class folder contains:

```
class<N>/
├── index.html              ← chapter list for this class
├── lesson-shared.js        ← shared CSS + TTS engine
├── 01_<ChapterName>/
│   ├── lesson.html         ← vocabulary table
│   └── exercise.html       ← Q&A exercises
├── 02_<ChapterName>/
│   ├── lesson.html
│   └── exercise.html
└── ...
```

Every `lesson.html` and `exercise.html` loads `lesson-shared.js` from its parent class directory:

```html
<script src="../lesson-shared.js"></script>
```

This single script injects the font, all CSS, and the TTS engine — no duplication across chapters.

---

## 4. Repository Layout

```
telugu4nontelugu/
├── app/
│   └── src/main/
│       ├── assets/                  ← WebView content root
│       │   ├── index.html
│       │   ├── style.css
│       │   ├── class5/
│       │   ├── class6/
│       │   └── class8/
│       └── java/com/telugu4nontelugu/   ← Android Kotlin source
├── class5/                          ← source/draft content (not served)
├── class6/                          ← source/draft content (not served)
├── scripts/                         ← Python helper scripts
│   ├── build_html.py
│   ├── extract_pdf_images.py
│   └── translate_chapters.py
├── templates/                       ← HTML templates for new pages
│   ├── lesson_template.html
│   ├── exercise_template.html
│   ├── chapter_template.html
│   └── index_template.html
├── docs/                            ← GitHub Pages mirror
├── PRODUCT_MANUAL.md                ← this file
├── build.gradle.kts
└── settings.gradle.kts
```

> The `class5/` and `class6/` folders at the root are source/working directories containing PDFs, markdown drafts, and translation files. **They are not served to the app.** Only content under `app/src/main/assets/` is bundled into the APK.

---

## 5. Pages & Navigation

### Home screen (`index.html`)

The home screen lists every class as a card. Active classes are clickable links; upcoming classes display a "Soon" badge and are non-interactive.

```
🐯 Telugu Buddy
─────────────────────────────
[Active]  🏞️  Class 5 — Tenepalukulu 5        → class5/index.html
[Active]  🏰  Class 6 — Nawa Vasantam 1       → class6/index.html
[Active]  🚀  Class 8 — Nawa Vasantam 3       → class8/index.html

Coming Soon
[Soon]    🌱  Class 1 — Jabili 1
[Soon]    🌿  Class 2 — Jabili 2
[Soon]    🌷  Class 3 — Jabili 3
[Soon]    🌳  Class 4 — Jabili 4
[Soon]    🌏  Class 7 — Nawa Vasantam 2
```

### Class index (`class<N>/index.html`)

Lists all chapters for the class. Each row shows the chapter title in both English transliteration and Telugu script, with two buttons:

- **Read Story** → `lesson.html`
- **Do Exercises** → `exercise.html`

A **← Back to Class Selection** link returns to the home screen.

### Navigation flow

```
Home (index.html)
  └─► Class index (class<N>/index.html)
        ├─► Lesson  (class<N>/NN_Name/lesson.html)   [← Back to Chapter Selection]
        └─► Exercise (class<N>/NN_Name/exercise.html) [← Back to Chapter Selection]
```

---

## 6. Lesson Pages (`lesson.html`)

Each lesson page presents the chapter's vocabulary and key sentences in a **4-column table**:

| Column | Content |
|--------|---------|
| Telugu | Telugu script (uses Noto Sans Telugu font) |
| Pronunciation | Romanized phonetic guide |
| Meaning | English definition or context sentence |
| 🔊 | Speak button — calls `speakTelugu(text, button)` |

Pages are divided by section headings (`div.section-heading`) that correspond to textbook page numbers or scene descriptions, e.g. `📖 Page 2 — Scene 1: People at Home`.

### Example row

```html
<tr>
    <td>వనజ</td>
    <td>Vanaja</td>
    <td>Vanaja — the mother, combing her daughter's hair</td>
    <td><button class="speak-btn" onclick="speakTelugu('వనజ', this)">🔊</button></td>
</tr>
```

### Page header

```html
<header>
    <h1>ఇల్లు</h1>
    <p class="subtitle">Chapter 1 &nbsp;|&nbsp; Illu (The Home) &nbsp;|&nbsp; Class 6 Telugu</p>
</header>
```

The subtitle always shows: chapter number | transliteration (English title) | class.

---

## 7. Exercise Pages (`exercise.html`)

Each exercise page contains **6 `qa-block` sections**, one per comprehension question or activity. The blocks are self-contained: each has a header with the question/prompt and a body with the answer.

### `qa-block` anatomy

```html
<div class="qa-block">
    <div class="qa-header">
        <span class="section-label">Q1</span>
        <span class="qa-text">
            Question text in Telugu / English
            <button class="speak-btn" onclick="speakTelugu('...', this)">🔊</button>
        </span>
    </div>
    <div class="qa-body">
        Answer content — may include tables, lists, or plain text
    </div>
</div>
```

The orange gradient header (`qa-header`) visually separates each question. All Telugu text in both questions and answers has a `🔊` speak button.

### Typical 6-block structure (varies by chapter type)

| Block | Typical content |
|-------|----------------|
| Q1 | Character/subject identification |
| Q2 | Key event or action in the story |
| Q3 | Deeper comprehension (why/how) |
| Q4 | Context-specific detail or dialogue |
| Q5 | Vocabulary list with meanings |
| Q6 | Moral, poet info, or completion activity |

---

## 8. Shared Resource: `lesson-shared.js`

Every `lesson.html` and `exercise.html` loads one shared JavaScript file from the class root:

```html
<script src="../lesson-shared.js"></script>
```

This file injects three things at parse time (before the page renders):

### 1. Google Font — Noto Sans Telugu

```js
const link = document.createElement('link');
link.href = 'https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600&display=swap';
document.head.appendChild(link);
```

Noto Sans Telugu ensures correct Telugu glyph rendering on all Android versions. It requires an internet connection on first load; after that the browser may cache it.

### 2. Shared CSS

All layout, table, button, and responsive styles are injected via `document.createElement('style')`. Key CSS classes:

| Class | Purpose |
|-------|---------|
| `.container` | Max-width 980 px white card with drop shadow |
| `.section-heading` | Orange-bordered section title |
| `table` | Vocabulary table — striped rows, borders |
| `.speak-btn` | Round orange button with pulse animation when speaking |
| `.qa-block` | Exercise card with shadow |
| `.qa-header` | Orange gradient title bar inside a qa-block |
| `.section-label` | Small numbered badge in qa-header |
| `.qa-text` | Question text area |
| `.back-button` | "← Back" link styled in brand red |
| `.page-note` | Small grey source-page citation |

### 3. TTS Engine

Exposes `window.speakTelugu(text, button)` globally so any inline `onclick` can call it. See the next section for full details.

---

## 9. Text-to-Speech Engine

The TTS engine uses a **3-tier fallback** strategy so pronunciation works in as many environments as possible.

```
speakTelugu(text, btn)
       │
       ├── Tier 1 ── Web Speech API (native te-IN voice)
       │           Offline. Works on devices with a Telugu TTS pack installed
       │           (most modern Android + Google TTS).
       │
       ├── Tier 2 ── Sound of Text API
       │           Online fallback. POSTs to api.soundoftext.com → Google Cloud TTS
       │           Polls for the audio URL → plays via <audio> element.
       │           No API key required.
       │
       └── Tier 3 ── Silent fail
                   Shows ⚠️ on the button for 3 seconds, then resets to 🔊.
                   Title tooltip explains the issue.
```

### Tier 1 — Web Speech API

```js
const utt = new SpeechSynthesisUtterance(text);
utt.voice = teluguVoice;   // lang: 'te-IN'
utt.lang = 'te-IN';
utt.rate = 0.85;
window.speechSynthesis.speak(utt);
```

Voice detection happens at page load (`speechSynthesis.onvoiceschanged`). If no `te-IN` or `te-*` voice is found, Tier 1 is skipped automatically.

### Tier 2 — Sound of Text API

```js
// Step 1: request generation
POST https://api.soundoftext.com/sounds
Body: { engine: "Google", data: { text, voice: "te" } }

// Step 2: poll for completion (up to 8 × 700 ms)
GET https://api.soundoftext.com/sounds/{id}
// Response: { status: "Done", location: "<S3-URL>" }

// Step 3: play via <audio id="tts-audio">
audio.src = location;
audio.play();
```

This uses Google Cloud TTS under the hood via a free CORS-enabled proxy — no API key needed.

### Button visual feedback

| State | Appearance |
|-------|-----------|
| Idle | 🔊 orange button |
| Speaking | 🔊 pulsing animation (`.speaking` class) |
| Error | ⚠️ for 3 seconds, then resets |

---

## 10. Responsive Design

The app is fully optimized for mobile use in an Android WebView.

### Viewport meta tag (all pages)

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
```

`user-scalable=no` and `maximum-scale=1.0` prevent pinch-zoom, which is intentional for a controlled learning app experience.

### Breakpoints

All responsive overrides target `@media (max-width: 600px)`.

**Lesson/exercise pages** (via `lesson-shared.js`):

| Element | Desktop | Mobile (≤600 px) |
|---------|---------|-----------------|
| `body` | `padding: 20px` | `padding: 10px` |
| `h1` | `font-size: 2em` | `font-size: 1.5em` |
| `table` | auto layout | `table-layout: fixed` |
| `td` | normal padding | `padding: 8px 6px; font-size: 0.88em` |
| Telugu column | auto | 22% width, `font-size: 1em` |
| `.qa-header` | row | `flex-wrap: wrap; gap: 8px` |
| `.grid-container` | many columns | max 2 columns |

**Index pages** (class `index.html` inline styles):

| Element | Desktop | Mobile (≤600 px) |
|---------|---------|-----------------|
| `h1` | `2.5em` | `1.8em` |
| `.chapter-card` | row (space-between) | column, items left-aligned |
| `.buttons` | flex row | `width: 100%; flex-wrap: wrap` |
| `.button` | `padding: 10px 20px` | `padding: 9px 14px; font-size: 0.9em` |

---

## 11. Available Content by Class

### Class 5 — Tenepalukulu 5 (10 chapters)

| # | Folder | English Title |
|---|--------|--------------|
| 1 | `01_Pandem` | Pandem |
| 2 | `02_Samaikya_Bharati` | Samaikya Bharati |
| 3 | `03_Rekkala_Enugu` | Rekkala Enugu (The Winged Elephant) |
| 4 | `04_Parishubhrata` | Parishubhrata (Cleanliness) |
| 5 | `05_Nirmal_Bommalu` | Nirmal Bommalu (Nirmal Dolls) |
| 6 | `06_Shataka_Padyalu` | Shataka Padyalu (Shatakam Verses) |
| 7 | `07_Sankranthi_Sandesham` | Sankranthi Sandesham (Sankranti Message) |
| 8 | `08_Kanuvippu` | Kanuvippu (Eye-Opener) |
| 9 | `09_Ramappa` | Ramappa |
| 10 | `10_Shibi_Chakravarti` | Shibi Chakravarti |

### Class 6 — Nawa Vasantam 1 (10 chapters)

| # | Folder | Telugu Title | English Title |
|---|--------|-------------|--------------|
| 1 | `01_Illu` | ఇల్లు | The Home |
| 2 | `02_Manamantaa_Okkate` | మనమంతా ఒక్కటే | We Are All One |
| 3 | `03_Vanaakalam` | వానాకాలం | The Rainy Season |
| 4 | `04_Chitti_Mokka` | చిట్టి మొక్క | The Little Sapling |
| 5 | `05_Kothi_Buddhi` | కోతి బుద్ధి | Monkey Wisdom |
| 6 | `06_Amma` | అమ్మ | Mother (Poem) |
| 7 | `07_Simham_Kundelu` | సింహం – కుందేలు | The Lion and the Rabbit |
| 8 | `08_Warangal` | వరంగల్ | Warangal (Letter format) |
| 9 | `09_Selfon` | సెల్ఫోన్ | Cell Phone |
| 10 | `10_Neethi_Padyalu` | నీతి పద్యాలు | Moral Verses |

### Class 8 — Nawa Vasantam 3 (8 chapters)

| # | Folder | Telugu Title | English Title |
|---|--------|-------------|--------------|
| 1 | `01_Chaduvedam` | చదువుదాం | Let Us Study (Patriotic poem) |
| 2 | `02_Murkulu` | మూర్ఖులు | The Fools (Story) |
| 3 | `03_Papa_Palukulu` | పాప పలుకులు | Children's Words (Poem) |
| 4 | `04_Spoorti` | స్ఫూర్తి | Inspiration (Letter about blind teacher) |
| 5 | `05_Shataka_Sudha` | శతక సుధ | Nectar of Shatakams (Verses) |
| 6 | `06_Varahala_Vaana` | వరాహాల వాన | Rain of Deceit (Dialogue) |
| 7 | `07_Simham_Gadida` | సింహం - గాడిద | The Lion and the Donkey |
| 8 | `08_Balyamithrulu` | బాల్యమిత్రులు | Childhood Friends (Story) |

---

## 12. Build & Deploy

### Prerequisites

- Android Studio (Hedgehog or later) or `gradle` CLI
- JDK 8+
- Android SDK with API 35 platform

### Build release APK

```bash
# From the repo root
./gradlew assembleRelease
```

Output: `app/build/outputs/apk/release/Telugubuddy.apk`

The release build has minification and resource shrinking enabled (ProGuard). The resulting APK is self-contained — all HTML/CSS/JS is bundled inside.

### Install on device

```bash
adb install app/build/outputs/apk/release/Telugubuddy.apk
```

Or copy the APK to the device and open it (enable "Install from unknown sources" if not from Play Store).

### Content-only update (no Kotlin change)

Edit files under `app/src/main/assets/`, then rebuild. No Kotlin code needs to change for content updates.

---

## 13. Adding a New Class or Chapter

### Add a new class

1. Create `app/src/main/assets/class<N>/` directory.
2. Copy `lesson-shared.js` from an existing class into it.
3. Create `class<N>/index.html` from [`templates/index_template.html`](templates/index_template.html) — update the header title and chapter list.
4. Add a card to `app/src/main/assets/index.html`:

```html
<a href="class<N>/index.html" class="card active">
    <span class="badge ready">Active</span>
    <span class="icon">🎯</span>
    <div class="card-content">
        <span class="class-title">Class N</span>
        <span class="book-name">Book Title Here</span>
    </div>
</a>
```

5. Remove the old "Soon" card for that class if one exists.

### Add a new chapter to an existing class

1. Create `app/src/main/assets/class<N>/NN_ChapterName/`.
2. Create `lesson.html` using [`templates/lesson_template.html`](templates/lesson_template.html):
   - `<script src="../lesson-shared.js"></script>` in `<head>`
   - `<h1>Telugu title</h1>` in `<header>`
   - Subtitle: `Chapter N | Transliteration (English) | Class N Telugu`
   - One `<table>` per textbook page/scene section
   - Each row: Telugu | Pronunciation | Meaning | `<button onclick="speakTelugu('Telugu', this)">🔊</button>`
3. Create `exercise.html` using [`templates/exercise_template.html`](templates/exercise_template.html):
   - Same `<script src="../lesson-shared.js"></script>` and header structure
   - 6 `qa-block` divs, one per comprehension question
   - All Telugu text gets a `🔊` speak button
4. Add the chapter card to `class<N>/index.html`:

```html
<div class="chapter-card">
    <span class="chapter-title">N. Title (తెలుగు పేరు)</span>
    <div class="buttons">
        <a href="NN_ChapterName/lesson.html" class="button">Read Story</a>
        <a href="NN_ChapterName/exercise.html" class="button">Do Exercises</a>
    </div>
</div>
```

### lesson.html checklist

- [ ] `<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">`
- [ ] `<script src="../lesson-shared.js"></script>` — no inline styles needed
- [ ] Header with Telugu chapter name in `<h1>`
- [ ] `<a href="../index.html" class="back-button">← Back to Chapter Selection</a>`
- [ ] `<p class="page-note">Source: Textbook pages X–Y …</p>`
- [ ] At least one `<div class="section-heading">` per page/scene group
- [ ] Each vocab row ends with `<td><button class="speak-btn" onclick="speakTelugu('', this)">🔊</button></td>`

### exercise.html checklist

- [ ] Same viewport and `lesson-shared.js` script tag
- [ ] Same orange gradient header
- [ ] Exactly 6 `qa-block` divs
- [ ] `qa-header` contains `section-label` (Q1…Q6) + `qa-text` with question
- [ ] All Telugu strings in `qa-header` and `qa-body` have speak buttons
- [ ] `<a href="../index.html" class="back-button">` at the top

---

## 14. Troubleshooting

### Telugu text not rendering

**Symptom:** Boxes or question marks instead of Telugu characters.  
**Cause:** Noto Sans Telugu font not loaded (no internet, or Google Fonts blocked).  
**Fix:** The font loads from `https://fonts.googleapis.com`. Ensure the WebView allows internet access. The font renders on first load and may be cached after that.

### 🔊 button shows ⚠️ after tapping

**Symptom:** Button briefly shows ⚠️ then reverts to 🔊.  
**Cause:** Both TTS tiers failed — either no te-IN voice installed (Tier 1) and no internet connection (Tier 2).  
**Fix:**
- Install the Google Telugu TTS pack (Settings → Accessibility → TTS Output → Google TTS Engine → Install language data → Telugu).
- Or ensure the device has internet access for the Sound of Text fallback.

### Pages look too small / too large on device

**Symptom:** Layout is zoomed in or out.  
**Cause:** Viewport meta tag missing or wrong.  
**Fix:** Every page must include:
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
```

### Chapter card links to a missing page (404 / blank WebView)

**Symptom:** Tapping "Read Story" shows a blank or error page.  
**Cause:** `lesson.html` or `exercise.html` missing from the assets folder.  
**Fix:** Check that the file exists at the path listed in `class<N>/index.html`. If a chapter is not yet ready, remove or disable its card temporarily.

### Table overflows horizontally on mobile

**Symptom:** Horizontal scroll appears inside a lesson table.  
**Cause:** Long Meaning column text without break opportunities.  
**Fix:** `lesson-shared.js` already sets `table-layout: fixed` and `word-break: break-word` on mobile. If still overflowing, shorten the English meaning text or split into two rows.

### Build fails with ProGuard errors

**Cause:** Resource shrinking removed a class or asset.  
**Fix:** All user-visible content is in `assets/` and is not subject to ProGuard or resource shrinking. If a Kotlin class is stripped, add a `@Keep` annotation or update `proguard-rules.pro`.

---

*Last updated: 2026-06-23*
