/**
 * lesson-shared.js
 * ─────────────────────────────────────────────────────────────────────────────
 * Shared resources for every Class 6 lesson page.
 * Injected at <head> parse time via <script src="../lesson-shared.js">.
 *
 * Provides:
 *   1. Google Fonts  — Noto Sans Telugu
 *   2. CSS           — full layout, table, speaker-button styling
 *   3. TTS engine    — speakTelugu(text, btn)  ← call from onclick
 * ─────────────────────────────────────────────────────────────────────────────
 */

/* ── 1. Google Fonts ─────────────────────────────────────────────────────── */
(function injectFonts() {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600&display=swap';
    document.head.appendChild(link);
})();

/* ── 2. Shared CSS ───────────────────────────────────────────────────────── */
(function injectStyles() {
    const style = document.createElement('style');
    style.textContent = `
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f4f8;
            margin: 0;
            padding: 20px;
        }

        header {
            background: linear-gradient(135deg, #FF9966 0%, #FF5E62 100%);
            color: white;
            padding: 20px;
            border-radius: 20px;
            margin-bottom: 20px;
            text-align: center;
        }

        h1 { margin: 0; font-size: 2em; }

        .subtitle {
            margin: 6px 0 0;
            font-size: 1em;
            opacity: 0.9;
        }

        .container {
            max-width: 980px;
            margin: 0 auto;
            background: white;
            padding: 24px;
            border-radius: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
        }

        .section-heading {
            font-size: 1.1em;
            font-weight: bold;
            color: #FF5E62;
            margin: 28px 0 8px;
            border-bottom: 2px solid #FFD0B0;
            padding-bottom: 4px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }

        th, td {
            padding: 12px 14px;
            border: 1px solid #ddd;
            text-align: left;
            vertical-align: middle;
        }

        th {
            background-color: #FF9966;
            color: white;
            font-size: 0.95em;
        }

        td:first-child {
            font-family: 'Noto Sans Telugu', sans-serif;
            font-size: 1.2em;
            font-weight: 600;
        }

        td:nth-child(2) {
            font-style: italic;
            color: #444;
        }

        td:nth-child(4) {
            text-align: center;
            width: 56px;
        }

        tr:nth-child(even) { background-color: #fdf5f0; }

        /* ── Speaker button ── */
        .speak-btn {
            background: none;
            border: 2px solid #FF9966;
            border-radius: 50%;
            width: 38px;
            height: 38px;
            font-size: 1.1em;
            cursor: pointer;
            transition: background 0.2s, transform 0.15s;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
        }
        .speak-btn:hover {
            background: #FF9966;
            transform: scale(1.1);
        }
        .speak-btn.speaking {
            background: #FF5E62;
            border-color: #FF5E62;
            animation: ls-pulse 0.6s infinite alternate;
        }
        @keyframes ls-pulse {
            from { transform: scale(1);    }
            to   { transform: scale(1.15); }
        }

        .back-button {
            display: inline-block;
            margin-top: 24px;
            text-decoration: none;
            color: #FF5E62;
            font-weight: bold;
        }
        .back-button:hover { color: #FF9966; }

        .page-note {
            font-size: 0.82em;
            color: #999;
            margin-top: 4px;
        }
    `;
    document.head.appendChild(style);
})();

/* ── 3. TTS engine ───────────────────────────────────────────────────────── */
(function initTTS() {
    // Inject hidden audio element used by the CORS-proxy fallback
    const audio = document.createElement('audio');
    audio.id = 'tts-audio';
    audio.style.display = 'none';
    document.addEventListener('DOMContentLoaded', () => document.body.appendChild(audio));

    let teluguVoice = null;

    function loadVoices() {
        const voices = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
        teluguVoice = voices.find(v => v.lang === 'te-IN' || v.lang.startsWith('te')) || null;
    }
    if ('speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = loadVoices;
        loadVoices();
    }

    function setBtnState(btn, speaking) {
        document.querySelectorAll('.speak-btn').forEach(b => b.classList.remove('speaking'));
        if (speaking) btn.classList.add('speaking');
    }

    async function playViaProxy(text, btn) {
        // ── Sound of Text API ─────────────────────────────────────────────
        // Uses Google Cloud TTS under the hood, has proper CORS headers,
        // supports te-IN, free with no API key.
        // Step 1: request audio generation
        try {
            const resp = await fetch('https://api.soundoftext.com/sounds', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ engine: 'Google', data: { text, voice: 'te' } })
            });
            if (!resp.ok) throw new Error('sot_request');
            const { id, success } = await resp.json();
            if (!success || !id) throw new Error('sot_no_id');

            // Step 2: poll until the audio file is ready (usually < 1 s)
            for (let attempt = 0; attempt < 8; attempt++) {
                await new Promise(r => setTimeout(r, 700));
                const statusResp = await fetch(`https://api.soundoftext.com/sounds/${id}`);
                if (!statusResp.ok) continue;
                const { status, location } = await statusResp.json();
                if (status === 'Done' && location) {
                    // Step 3: play the S3 audio URL (CORS-enabled)
                    audio.src = location;
                    audio.onended = () => setBtnState(btn, false);
                    audio.onerror = () => setBtnState(btn, false);
                    await audio.play();
                    return;                       // ✅ success
                }
                if (status === 'Error') throw new Error('sot_error');
            }
            throw new Error('sot_timeout');

        } catch (_) {
            // Tier 3: silent fail — show ⚠️ on the button for 3 s
            setBtnState(btn, false);
            btn.title = '⚠️ Audio unavailable — check internet connection';
            btn.textContent = '⚠️';
            setTimeout(() => {
                btn.textContent = '🔊';
                btn.title = 'Pronounce in Telugu';
            }, 3000);
        }
    }

    // Exposed globally so onclick="speakTelugu(...)" works in HTML
    window.speakTelugu = function speakTelugu(text, btn) {
        window.speechSynthesis && window.speechSynthesis.cancel();
        if (audio._objectUrl) { URL.revokeObjectURL(audio._objectUrl); audio._objectUrl = null; }
        audio.pause();
        audio.src = '';

        setBtnState(btn, true);

        // Tier 1 — native te-IN voice (offline)
        if ('speechSynthesis' in window && teluguVoice) {
            loadVoices();
            const utt = new SpeechSynthesisUtterance(text);
            utt.voice = teluguVoice;
            utt.lang = 'te-IN';
            utt.rate = 0.85;
            utt.onend = () => setBtnState(btn, false);
            utt.onerror = () => { setBtnState(btn, false); playViaProxy(text, btn); };
            window.speechSynthesis.speak(utt);
            return;
        }

        // Tier 2 — CORS-proxied Google TTS (online, same page)
        playViaProxy(text, btn);
    };
})();
