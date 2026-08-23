"""
transcript.py
--------------
Handles multilingual speech-to-text (Whisper, supports Hindi/Marathi/English
out of the box) and a lightweight context-risk layer that scans the
transcript for phrases commonly used in impersonation / social-engineering
scam calls.

Whisper is loaded lazily and wrapped in a try/except: if the model can't be
downloaded (e.g. no internet at the moment you're testing), the API still
responds using a graceful fallback instead of crashing the demo.
"""

_whisper_model = None

# Risk keywords per language (lowercase substrings to match against transcript)
RISK_KEYWORDS = {
    "en": ["otp", "one time password", "transfer", "urgent", "freeze", "frozen",
           "verify your identity", "immediately", "account will be", "share the code",
           "digital arrest", "warrant", "blocked"],
    "hi": ["ओटीपी", "otp", "ट्रांसफर", "अभी", "फ्रीज़", "फ्रीज", "वेरीफाई",
           "जल्दी", "गिरफ्तार", "वारंट", "ब्लॉक"],
    "mr": ["ओटीपी", "otp", "ट्रान्सफर", "लगेच", "गोठव", "वेरिफाय",
           "अटक", "वॉरंट", "ब्लॉक"],
}


def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        import whisper
        # "tiny" is fastest to download (~75MB) and enough for a hackathon demo.
        # Swap to "base" or "small" for better accuracy if you have more time/bandwidth.
        _whisper_model = whisper.load_model("tiny")
    return _whisper_model


def transcribe(path: str, language_hint: str | None = None) -> dict:
    """
    Returns: {"text": str, "language": str, "segments": [...] } or a graceful
    fallback dict with "error" set if Whisper isn't available.
    """
    try:
        model = _get_whisper_model()
        lang_map = {"en": "en", "hi": "hi", "mr": "mr"}
        options = {}
        if language_hint in lang_map:
            options["language"] = lang_map[language_hint]
        result = model.transcribe(path, **options)
        return {
            "text": result.get("text", "").strip(),
            "language": result.get("language", language_hint or "en"),
            "ok": True,
        }
    except Exception as e:  # noqa: BLE001 - intentional broad catch for demo resilience
        return {
            "text": "",
            "language": language_hint or "en",
            "ok": False,
            "error": str(e),
        }


def score_context(text: str, language: str) -> tuple[float, list[str]]:
    """
    Returns (context_risk_score 0-100, matched_keywords).
    Simple substring match — fast, transparent, no extra ML dependency.
    """
    if not text:
        return 0.0, []

    lower = text.lower()
    keywords = RISK_KEYWORDS.get(language, RISK_KEYWORDS["en"])
    matched = [kw for kw in keywords if kw.lower() in lower]

    if not matched:
        return 0.0, []

    # More matches -> higher context risk, capped at 100
    score = min(100.0, 25.0 * len(matched))
    return score, matched


def build_flagged_transcript(text: str, language: str) -> list[dict]:
    """
    Splits transcript into segments, marking risk-keyword spans as flagged,
    for the frontend's highlighted-transcript view.
    """
    if not text:
        return []

    keywords = sorted(RISK_KEYWORDS.get(language, RISK_KEYWORDS["en"]), key=len, reverse=True)
    lower = text.lower()
    spans = []  # (start, end)
    for kw in keywords:
        start = 0
        kwl = kw.lower()
        while True:
            idx = lower.find(kwl, start)
            if idx == -1:
                break
            spans.append((idx, idx + len(kw)))
            start = idx + len(kw)

    if not spans:
        return [{"text": text, "flagged": False}]

    spans.sort()
    merged = [spans[0]]
    for s, e in spans[1:]:
        if s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))

    segments = []
    cursor = 0
    for s, e in merged:
        if s > cursor:
            segments.append({"text": text[cursor:s], "flagged": False})
        segments.append({"text": text[s:e], "flagged": True})
        cursor = e
    if cursor < len(text):
        segments.append({"text": text[cursor:], "flagged": False})

    return segments
