/**
 * lesson-shared.js
 * ─────────────────────────────────────────────────────────────────────────────
 * Shared resources for Telugu lessons and worksheets.
 * Injected at <head> parse time via <script src="../lesson-shared.js"></script>.
 *
 * Provides:
 *   1. Google Fonts  — Noto Sans Telugu & Poppins
 *   2. CSS           — full layout, tables, speaker-button & interactive word styling
 *   3. TTS engine    — speakTelugu(text, btn), speakWord(word, elem), stopAllSpeech()
 *                      Hybrid: Native Web Speech API (offline) + Fast Google Cloud TTS (Sound of Text) with caching
 * ─────────────────────────────────────────────────────────────────────────────
 */

/* ── 1. Google Fonts ─────────────────────────────────────────────────────── */
(function injectFonts() {
    if (document.getElementById('telugu-fonts')) return;
    const link = document.createElement('link');
    link.id = 'telugu-fonts';
    link.rel = 'stylesheet';
    link.href = 'https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600;700&family=Poppins:wght@400;500;600;700&display=swap';
    document.head.appendChild(link);
})();

/* ── 2. Shared CSS ───────────────────────────────────────────────────────── */
(function injectStyles() {
    if (document.getElementById('telugu-shared-styles')) return;
    const style = document.createElement('style');
    style.id = 'telugu-shared-styles';
    style.textContent = `
        body {
            font-family: 'Poppins', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
            vertical-align: middle;
        }
        .speak-btn:hover {
            background: #FF9966;
            transform: scale(1.1);
        }
        .speak-btn.speaking {
            background: #FF5E62;
            border-color: #FF5E62;
            color: white;
            animation: ls-pulse 0.6s infinite alternate;
        }
        @keyframes ls-pulse {
            from { transform: scale(1);    }
            to   { transform: scale(1.15); }
        }

        /* ── Clickable words ── */
        .t-word {
            cursor: pointer;
            border-bottom: 1.5px dotted #FF9966;
            border-radius: 4px;
            padding: 1px 4px;
            transition: all 0.2s ease;
        }
        .t-word:hover {
            background-color: #fff3eb;
            color: #c53030;
            border-bottom: 1.5px solid #FF5E62;
        }
        .t-word.speaking-word {
            background-color: #fed7d7 !important;
            color: #9b2c2c !important;
            border-bottom: 2px solid #e53e3e !important;
            animation: ls-word-glow 0.8s infinite alternate;
        }
        @keyframes ls-word-glow {
            from { box-shadow: 0 0 4px rgba(255, 94, 98, 0.4); }
            to   { box-shadow: 0 0 10px rgba(255, 94, 98, 0.8); }
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

        /* ── Mobile Responsive ─────────────────────────────────────────────── */
        @media (max-width: 600px) {
            body { padding: 10px; }
            h1 { font-size: 1.5em; }
            .container {
                padding: 16px;
                border-radius: 12px;
            }
            table { table-layout: fixed; }
            th, td {
                padding: 8px 6px;
                word-break: break-word;
                overflow-wrap: break-word;
                font-size: 0.88em;
            }
            td:first-child { font-size: 1em; width: 22%; }
            td:nth-child(2) { width: 25%; }
            td:nth-child(3) { width: 41%; }
            td:nth-child(4) { width: 12%; }
            .qa-header { flex-wrap: wrap; gap: 8px; }
            .section-label {
                white-space: normal !important;
                font-size: 0.8em !important;
            }
            .grid-container { grid-template-columns: repeat(2, 1fr) !important; }
            .letter-grid td {
                width: 40px !important;
                height: 40px !important;
                font-size: 1.1em;
            }
            .alphabet-table td { padding: 5px 4px !important; font-size: 0.9em; }
            div[style*="display: flex; gap: 20px"] {
                flex-direction: column !important;
                gap: 10px !important;
            }
            .sub-header { flex-wrap: wrap; font-size: 1em; }
            .ans-table th, .ans-table td {
                padding: 7px 6px !important;
                font-size: 0.85em;
            }
            .ans-table td:first-child { font-size: 0.95em !important; }
            .ans-table td:nth-child(4) { width: 44px !important; }
        }
    `;
    document.head.appendChild(style);
})();

/* ── 3. Unified Robust TTS Engine ─────────────────────────────────────────── */
(function initTTS() {
    let teluguVoice = null;
    let voicesReady = false;
    let currentPlaybackRate = 0.9;
    const ttsAudioCache = new Map();
    let activeSafetyTimer = null;

    function getAudioPlayer() {
        let audio = document.getElementById('tts-audio');
        if (!audio) {
            audio = document.createElement('audio');
            audio.id = 'tts-audio';
            audio.style.display = 'none';
            if (document.body) {
                document.body.appendChild(audio);
            } else {
                document.addEventListener('DOMContentLoaded', () => {
                    if (!document.getElementById('tts-audio')) {
                        document.body.appendChild(audio);
                    }
                });
            }
        }
        return audio;
    }

    function loadVoices() {
        if (!('speechSynthesis' in window)) return false;
        try {
            const voices = window.speechSynthesis.getVoices() || [];
            const found = voices.find(v => (v.lang && v.lang.toLowerCase().startsWith('te')) ||
                                           (v.name && v.name.toLowerCase().includes('telugu'))) || null;
            if (found) {
                teluguVoice = found;
                voicesReady = true;
                return true;
            }
            if (voices.length > 0) voicesReady = true;
        } catch (_) {}
        return false;
    }

    if ('speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = loadVoices;
        loadVoices();
    }

    function clearSpeakingVisuals() {
        document.querySelectorAll('.speak-btn').forEach(b => b.classList.remove('speaking'));
        document.querySelectorAll('.t-word').forEach(w => w.classList.remove('speaking-word'));
    }

    function setBtnState(btn, speaking) {
        clearSpeakingVisuals();
        if (speaking && btn) btn.classList.add('speaking');
    }

    function setWordState(elem, speaking) {
        clearSpeakingVisuals();
        if (speaking && elem) elem.classList.add('speaking-word');
    }

    function showToast(msg, ms) {
        let toast = document.getElementById('tts-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'tts-toast';
            toast.style.cssText = 'display:none;position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#2d3748;color:white;padding:10px 18px;border-radius:24px;font-size:0.88rem;z-index:9999;box-shadow:0 4px 14px rgba(0,0,0,0.25);max-width:90vw;text-align:center;pointer-events:none;';
            if (document.body) document.body.appendChild(toast);
        }
        toast.textContent = msg;
        toast.style.display = 'block';
        clearTimeout(showToast._t);
        showToast._t = setTimeout(() => { if (toast) toast.style.display = 'none'; }, ms || 3500);
    }

    function stopAllSpeech() {
        if (activeSafetyTimer) {
            clearTimeout(activeSafetyTimer);
            activeSafetyTimer = null;
        }
        if (window.speechSynthesis) {
            try { window.speechSynthesis.cancel(); } catch (_) {}
        }
        const audio = getAudioPlayer();
        if (audio) {
            audio.onended = null;
            audio.onerror = null;
            audio.pause();
            audio.src = '';
        }
        clearSpeakingVisuals();
    }

    async function playViaCloudTTS(text, onStart, onEnd) {
        const audio = getAudioPlayer();
        if (!audio) {
            clearSpeakingVisuals();
            onEnd && onEnd();
            return;
        }

        try {
            let audioUrl = ttsAudioCache.get(text);

            if (!audioUrl) {
                const resp = await fetch('https://api.soundoftext.com/sounds', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ engine: 'Google', data: { text: text, voice: 'te' } })
                });
                if (!resp.ok) throw new Error('Cloud TTS request failed');
                const data = await resp.json();
                if (!data || !data.success || !data.id) throw new Error('Cloud TTS no sound ID');

                const soundId = data.id;
                for (let attempt = 0; attempt < 8; attempt++) {
                    await new Promise(r => setTimeout(r, 250 + attempt * 100));
                    const statusResp = await fetch('https://api.soundoftext.com/sounds/' + soundId);
                    if (!statusResp.ok) continue;
                    const statusData = await statusResp.json();
                    if (statusData.status === 'Done' && statusData.location) {
                        audioUrl = statusData.location;
                        ttsAudioCache.set(text, audioUrl);
                        break;
                    }
                    if (statusData.status === 'Error') throw new Error('Cloud TTS generation error');
                }
            }

            if (!audioUrl) throw new Error('Cloud TTS timed out');

            onStart && onStart();
            audio.src = audioUrl;
            audio.playbackRate = currentPlaybackRate || 0.9;
            audio.onended = () => {
                clearSpeakingVisuals();
                onEnd && onEnd();
            };
            audio.onerror = () => {
                clearSpeakingVisuals();
                showToast('⚠️ ఆడియో లోడ్ కాలేదు (Audio failed to load)', 3000);
                onEnd && onEnd();
            };
            await audio.play();

        } catch (err) {
            console.warn('Cloud TTS error:', err);
            clearSpeakingVisuals();
            showToast('⚠️ ఆడియో అందుబాటులో లేదు - ఇంటర్నెట్ తనిఖీ చేయండి (Audio unavailable - check internet)', 3500);
            onEnd && onEnd();
        }
    }

    function speakGeneric(text, onStart, onEnd) {
        if (!text || !text.trim()) return;
        const cleanText = text.trim();

        stopAllSpeech();
        loadVoices();

        // Tier 1: Local device Telugu speech synthesis (instant & offline)
        if ('speechSynthesis' in window && teluguVoice) {
            onStart && onStart();
            const utt = new SpeechSynthesisUtterance(cleanText);
            utt.voice = teluguVoice;
            utt.lang = 'te-IN';
            utt.rate = currentPlaybackRate || 0.9;

            let finished = false;
            utt.onend = () => {
                if (finished) return;
                finished = true;
                if (activeSafetyTimer) { clearTimeout(activeSafetyTimer); activeSafetyTimer = null; }
                clearSpeakingVisuals();
                onEnd && onEnd();
            };

            utt.onerror = (e) => {
                if (finished) return;
                finished = true;
                if (activeSafetyTimer) { clearTimeout(activeSafetyTimer); activeSafetyTimer = null; }
                console.warn('Web Speech error, falling back to Cloud TTS:', e);
                playViaCloudTTS(cleanText, onStart, onEnd);
            };

            const timeoutMs = Math.max(3500, cleanText.length * 160);
            activeSafetyTimer = setTimeout(() => {
                if (!finished && window.speechSynthesis.speaking) {
                    // Still speaking
                }
            }, timeoutMs);

            try {
                window.speechSynthesis.speak(utt);
                return;
            } catch (err) {
                console.warn('speechSynthesis.speak failed:', err);
            }
        }

        // Tier 2: Cloud Google TTS proxy (supports all devices/browsers with authentic Telugu audio)
        playViaCloudTTS(cleanText, onStart, onEnd);
    }

    // Globally exposed APIs
    window.speakWord = function(word, elem) {
        speakGeneric(word, () => setWordState(elem, true), () => clearSpeakingVisuals());
    };

    window.speakTelugu = function(text, btn) {
        speakGeneric(text, () => setBtnState(btn, true), () => clearSpeakingVisuals());
    };

    window.stopAllSpeech = stopAllSpeech;

    window.setPlaybackRate = function(rate, btn) {
        currentPlaybackRate = rate;
        document.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
        if (btn) btn.classList.add('active');
        const audio = getAudioPlayer();
        if (audio) audio.playbackRate = rate;
    };
})();
