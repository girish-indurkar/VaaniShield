# VaaniShield — Real-Time Voice Cloning Detection (SIH Project)

Two folders:
- `voiceshield/` — Next.js frontend (the dashboard UI)
- `voiceshield-backend/` — Python FastAPI backend (detection engine + multilingual STT)

---

## 1. Backend Setup (do this first)

```bash
cd voiceshield-backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

Check it's alive: open `http://localhost:8000/health` in a browser → should show `{"status":"ok"}`

> ⚠️ First time you run `/analyze`, Whisper will auto-download its model
> (~75MB for "tiny") — you need internet for that ONE time only. If you're
> on flaky hackathon WiFi, do this at home the night before so it's cached.

### Test it directly (no frontend needed) — 2 ready-made test files included:

```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@test_audio/sample_real_like.wav" \
  -F "language=en"

curl -X POST http://localhost:8000/analyze \
  -F "file=@test_audio/sample_cloned_like.wav" \
  -F "language=en"
```

`sample_real_like.wav` should score **low/safe**, `sample_cloned_like.wav`
should score **high/risk**. These are synthetically generated demo files
(programmatically made, since we can't ship real human recordings) — for
your actual judge demo, swap in:
- `sample_real_like.wav` → a real recording of your own voice
- `sample_cloned_like.wav` → output from any free TTS/voice-clone tool
  (ElevenLabs free tier, Coqui TTS, etc.) reading the same sentence

This will look far more convincing live than synthetic tones.

---

## 2. Frontend Setup

Open a **second terminal** (keep the backend running in the first one):

```bash
cd voiceshield
npm install
npm run dev
```

Open `http://localhost:3000`

- Upload `sample_cloned_like.wav` → click **Run Analysis** → should show a
  high red risk score with reasons listed.
- Upload `sample_real_like.wav` → should show a low green/safe score.
- If the backend isn't running, the app automatically falls back to demo
  (mock) data and shows a small warning — so your demo never fully breaks
  even if something goes wrong with the backend on stage.

---

## 3. How It Works (for your presentation)

1. **Voice authenticity engine** (`app/detection.py`) — extracts DSP
   features (pitch jitter, amplitude shimmer, spectral flatness, high-freq
   energy ratio) per 2-second chunk. These are well-documented indicators
   used in anti-spoofing research to separate natural speech from
   vocoder/TTS output.
2. **Multilingual transcription** (`app/transcript.py`) — OpenAI Whisper,
   supports Hindi / Marathi / English out of the box.
3. **Context risk layer** — scans the transcript for scam-associated
   phrases (OTP, urgent transfer, account freeze, etc.) in all 3 languages.
4. **Composite score** — 70% voice signal + 30% context signal → single
   0-100 risk score shown on the dashboard with full explainability.

## 4. What To Say If Asked "Why not a deep learning model?"

> "For the hackathon MVP we used an interpretable DSP-feature engine so the
> whole pipeline runs offline, on CPU, in real time, with every score fully
> explainable. Our architecture is designed so this layer is a drop-in
> replacement for a trained neural countermeasure model (e.g. AASIST on
> ASVspoof) in a production deployment — the API contract doesn't change."

---

## 5. Folder Structure

```
voiceshield/                  # Next.js frontend
  app/page.tsx                 # main dashboard
  components/RiskGauge.tsx
  components/Waveform.tsx
  lib/analysis.ts              # mock + real backend call

voiceshield-backend/          # FastAPI backend
  app/main.py                  # /analyze endpoint
  app/detection.py             # DSP-based voice authenticity engine
  app/transcript.py            # Whisper STT + keyword risk scoring
  test_audio/
    sample_real_like.wav
    sample_cloned_like.wav
  generate_test_audio.py       # script that made the above 2 files
  requirements.txt
```
