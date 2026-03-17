# Gemini Agent Instructions: Telugu4NonTelugu Android Build

## Project Goal
Convert this web-based repository into a high-performance, hybrid Android application (.apk) using a WebView container.

## Technical Guardrails
- **Language:** Kotlin with Jetpack Compose for the UI wrapper.
- **WebView Configuration:** - Enable JavaScript (crucial for `lesson-shared.js`).
    - Enable DOM storage and local file access.
    - Set `WebViewClient` to handle internal navigation within the app assets.
- **Asset Management:** All folders (`class5`, `class6`, `scanned_images`, `docs`) and files (`index.html`, `style.css`) must be moved to `app/src/main/assets/`.
- **Navigation:** Implement a back-button interceptor so the Android 'Back' button navigates the WebView history instead of closing the app.

## Autonomous Workflow
1. **Setup:** Initialize the Android project structure and update `build.gradle.kts` with necessary dependencies.
2. **Migration:** Move all relevant web assets into the assets folder.
3. **Coding:** Write the `MainActivity.kt` logic to load `file:///android_asset/index.html`.
4. **Debug Loop:** If the build fails due to SDK versions or missing libraries, resolve them autonomously and retry the build.
5. **Completion:** Once a stable Debug APK is generated, provide the local file path and a summary of the changes made.