// ---------------------------------------------------------------------------
// This file simulates what your Python (FastAPI + Whisper + AASIST) backend
// will return. Once your backend is ready, replace `runMockAnalysis` with a
// real fetch() call to e.g. POST http://localhost:8000/analyze
// and keep the same return shape so the UI doesn't need to change.
// ---------------------------------------------------------------------------

export type Lang = "en" | "hi" | "mr";

export type RiskBand = "safe" | "warning" | "risk";

export interface FlaggedReason {
  label: string;
  detail: string;
  weight: number; // 0-100 contribution to score
}

export interface Chunk {
  startSec: number;
  endSec: number;
  score: number; // 0-100 synthetic-likelihood for this chunk
}

export interface AnalysisResult {
  riskScore: number; // 0-100 overall
  band: RiskBand;
  chunks: Chunk[];
  reasons: FlaggedReason[];
  transcript: { text: string; flagged: boolean }[];
  language: Lang;
}

export function bandFor(score: number): RiskBand {
  if (score >= 70) return "risk";
  if (score >= 40) return "warning";
  return "safe";
}

const TRANSCRIPTS: Record<Lang, { text: string; flagged: boolean }[]> = {
  en: [
    { text: "Hi, this is your bank manager calling. ", flagged: false },
    { text: "Your account will be frozen ", flagged: true },
    { text: "in the next few minutes unless you ", flagged: false },
    { text: "share the OTP ", flagged: true },
    { text: "right now to verify your identity.", flagged: false },
  ],
  hi: [
    { text: "नमस्ते, मैं आपके बैंक से बोल रहा हूँ। ", flagged: false },
    { text: "आपका अकाउंट फ्रीज़ हो जाएगा ", flagged: true },
    { text: "अगर आप अभी ", flagged: false },
    { text: "OTP शेयर ", flagged: true },
    { text: "नहीं करते हैं।", flagged: false },
  ],
  mr: [
    { text: "नमस्कार, मी तुमच्या बँकेतून बोलतोय. ", flagged: false },
    { text: "तुमचं खातं गोठवलं जाईल ", flagged: true },
    { text: "जर तुम्ही लगेच ", flagged: false },
    { text: "OTP शेअर ", flagged: true },
    { text: "केला नाही तर.", flagged: false },
  ],
};

// ---------------------------------------------------------------------------
// REAL BACKEND CALL — used automatically once an audio file is uploaded.
// Points at the FastAPI backend (see /voiceshield-backend). Start it with:
//   uvicorn app.main:app --reload --port 8000
// ---------------------------------------------------------------------------
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function runRealAnalysis(
  file: File,
  language: Lang
): Promise<AnalysisResult> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("language", language);

  const res = await fetch(`${BACKEND_URL}/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error(`Backend error: ${res.status}`);
  }

  const data = await res.json();
  return {
    riskScore: data.riskScore,
    band: data.band,
    chunks: data.chunks,
    reasons: data.reasons,
    transcript: data.transcript,
    language,
  };
}

export function runMockAnalysis(language: Lang): AnalysisResult {
  const chunkCount = 8;
  const chunks: Chunk[] = Array.from({ length: chunkCount }).map((_, i) => {
    const base = 35 + Math.sin(i * 1.3) * 20 + Math.random() * 25;
    return {
      startSec: i * 2,
      endSec: i * 2 + 2,
      score: Math.max(5, Math.min(97, Math.round(base))),
    };
  });

  const riskScore = Math.round(
    chunks.reduce((a, c) => a + c.score, 0) / chunks.length
  );

  const reasons: FlaggedReason[] = [
    {
      label: "Unnatural pitch micro-variation",
      detail: "Prosody model detected flatter-than-human pitch contours between 4s–8s.",
      weight: 34,
    },
    {
      label: "Spectral discontinuity",
      detail: "High-frequency artifacts typical of neural vocoders found in 2 chunks.",
      weight: 28,
    },
    {
      label: "Urgency + OTP keywords",
      detail: "Transcript contains high-risk phrases commonly used in impersonation scams.",
      weight: 22,
    },
    {
      label: "Unknown caller, no voice history",
      detail: "No prior verified sample exists for cross-session comparison.",
      weight: 16,
    },
  ];

  return {
    riskScore,
    band: bandFor(riskScore),
    chunks,
    reasons,
    transcript: TRANSCRIPTS[language],
    language,
  };
}
