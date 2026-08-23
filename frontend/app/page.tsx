"use client";

import { useState } from "react";
import {
  ShieldAlert,
  UploadCloud,
  Mic,
  Play,
  Languages,
  AlertTriangle,
  CheckCircle2,
  PhoneCall,
} from "lucide-react";
import RiskGauge from "@/components/RiskGauge";
import Waveform from "@/components/Waveform";
import {
  AnalysisResult,
  Lang,
  runMockAnalysis,
  runRealAnalysis,
} from "@/lib/analysis";

const LANGUAGES: { code: Lang; label: string; native: string }[] = [
  { code: "en", label: "English", native: "EN" },
  { code: "hi", label: "Hindi", native: "हिं" },
  { code: "mr", label: "Marathi", native: "मर" },
];

export default function Home() {
  const [language, setLanguage] = useState<Lang>("en");
  const [status, setStatus] = useState<"idle" | "analyzing" | "done">("idle");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [selectedChunk, setSelectedChunk] = useState<number | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [backendError, setBackendError] = useState<string | null>(null);

  async function handleAnalyze() {
    setStatus("analyzing");
    setResult(null);
    setSelectedChunk(null);
    setBackendError(null);

    // If a real file was uploaded, call the actual backend.
    // Otherwise fall back to the mock demo data (useful before backend is running).
    if (file) {
      try {
        const r = await runRealAnalysis(file, language);
        setResult(r);
        setStatus("done");
        return;
      } catch (err) {
        setBackendError(
          "Couldn't reach the backend (is it running on :8000?). Showing demo data instead."
        );
        // fall through to mock below
      }
    }

    setTimeout(() => {
      const r = runMockAnalysis(language);
      setResult(r);
      setStatus("done");
    }, 1200);
  }

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-1 flex-col px-6 py-8">
      {/* Header */}
      <header className="mb-10 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#6c8cff]/15 text-[#6c8cff]">
            <ShieldAlert size={22} />
          </div>
          <div>
            <h1 className="font-display text-xl font-semibold tracking-tight">
              VaaniShield
            </h1>
            <p className="text-xs text-[#8b93a3]">
              Real-time voice authenticity &amp; impersonation risk engine
            </p>
          </div>
        </div>
        <div className="hidden items-center gap-2 rounded-full border border-[#1f2530] bg-[#12151c] px-3 py-1.5 text-xs text-[#8b93a3] sm:flex">
          <span className="h-1.5 w-1.5 rounded-full bg-[#2fd9a6]" />
          Engine online · edge-inference ready
        </div>
      </header>

      <div className="grid flex-1 grid-cols-1 gap-6 lg:grid-cols-[1.15fr_0.85fr]">
        {/* Left: Input + Waveform + Transcript */}
        <div className="flex flex-col gap-6">
          {/* Upload card */}
          <section className="rounded-2xl border border-[#1f2530] bg-[#12151c] p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-display text-sm font-semibold text-[#edeff3]">
                Call Audio
              </h2>
              <div className="flex items-center gap-1 rounded-lg border border-[#1f2530] bg-[#0d0f15] p-1">
                {LANGUAGES.map((l) => (
                  <button
                    key={l.code}
                    onClick={() => setLanguage(l.code)}
                    className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                      language === l.code
                        ? "bg-[#6c8cff] text-[#090b10]"
                        : "text-[#8b93a3] hover:text-[#edeff3]"
                    }`}
                  >
                    {l.native}
                  </button>
                ))}
              </div>
            </div>

            <label className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-[#2a3040] bg-[#0d0f15] py-8 text-center transition-colors hover:border-[#6c8cff]/60">
              <UploadCloud size={22} className="text-[#6c8cff]" />
              <span className="text-sm text-[#edeff3]">
                {fileName ?? "Upload a call recording, or drop it here"}
              </span>
              <span className="text-xs text-[#8b93a3]">WAV / MP3 · up to 5 min</span>
              <input
                type="file"
                accept="audio/*"
                className="hidden"
                onChange={(e) => {
                  const f = e.target.files?.[0] ?? null;
                  setFile(f);
                  setFileName(f?.name ?? null);
                }}
              />
            </label>

            {backendError && (
              <p className="mt-3 rounded-lg border border-[#f5a623]/30 bg-[#f5a623]/10 px-3 py-2 text-xs text-[#f5a623]">
                {backendError}
              </p>
            )}

            <div className="mt-4 flex gap-3">
              <button className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-[#1f2530] bg-[#0d0f15] py-2.5 text-sm text-[#edeff3] transition-colors hover:border-[#6c8cff]/50">
                <Mic size={16} /> Record live
              </button>
              <button
                onClick={handleAnalyze}
                disabled={status === "analyzing"}
                className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-[#6c8cff] py-2.5 text-sm font-medium text-[#090b10] transition-opacity hover:opacity-90 disabled:opacity-50"
              >
                <Play size={16} />
                {status === "analyzing" ? "Analyzing…" : "Run Analysis"}
              </button>
            </div>
          </section>

          {/* Waveform */}
          <section className="rounded-2xl border border-[#1f2530] bg-[#12151c] p-6">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="font-display text-sm font-semibold">
                Chunk-Level Synthetic-Likelihood
              </h2>
              {result && (
                <span className="font-mono text-xs text-[#8b93a3]">
                  {result.chunks.length} × 2s segments
                </span>
              )}
            </div>
            {result ? (
              <Waveform
                chunks={result.chunks}
                active={status === "done"}
                selected={selectedChunk}
                onSelect={setSelectedChunk}
              />
            ) : (
              <div className="flex h-28 items-center justify-center rounded-xl border border-[#1f2530] bg-[#0d0f15] text-sm text-[#8b93a3]">
                Run an analysis to see the live segment breakdown
              </div>
            )}
            {result && selectedChunk !== null && (
              <p className="mt-3 font-mono text-xs text-[#8b93a3]">
                Segment {result.chunks[selectedChunk].startSec}s–
                {result.chunks[selectedChunk].endSec}s ·{" "}
                <span className="text-[#edeff3]">
                  {result.chunks[selectedChunk].score}% synthetic-likelihood
                </span>
              </p>
            )}
          </section>

          {/* Transcript */}
          <section className="rounded-2xl border border-[#1f2530] bg-[#12151c] p-6">
            <div className="mb-3 flex items-center gap-2">
              <Languages size={16} className="text-[#6c8cff]" />
              <h2 className="font-display text-sm font-semibold">Live Transcript</h2>
            </div>
            {result ? (
              <p className="leading-relaxed text-[#c7cbd4]">
                {result.transcript.map((t, i) =>
                  t.flagged ? (
                    <span
                      key={i}
                      className="rounded bg-[#ff4757]/15 px-1 text-[#ff8a93]"
                    >
                      {t.text}
                    </span>
                  ) : (
                    <span key={i}>{t.text}</span>
                  )
                )}
              </p>
            ) : (
              <p className="text-sm text-[#8b93a3]">
                Transcript with flagged risk phrases will appear here after analysis.
              </p>
            )}
          </section>
        </div>

        {/* Right: Risk gauge + explainability */}
        <div className="flex flex-col gap-6">
          <section className="rounded-2xl border border-[#1f2530] bg-[#12151c] p-6">
            <h2 className="mb-5 font-display text-sm font-semibold">
              Composite Risk Score
            </h2>
            <div className="flex justify-center">
              {result ? (
                <RiskGauge score={result.riskScore} band={result.band} />
              ) : (
                <div className="flex h-52 w-52 items-center justify-center rounded-full border border-dashed border-[#2a3040] text-center text-xs text-[#8b93a3]">
                  Awaiting
                  <br />
                  analysis
                </div>
              )}
            </div>
            {result && result.band === "risk" && (
              <div className="mt-5 flex items-start gap-2 rounded-lg border border-[#ff4757]/30 bg-[#ff4757]/10 p-3 text-sm text-[#ff8a93]">
                <PhoneCall size={16} className="mt-0.5 shrink-0" />
                Recommended: pause the call, verify via a known callback number
                before sharing any information or approving a transfer.
              </div>
            )}
          </section>

          <section className="rounded-2xl border border-[#1f2530] bg-[#12151c] p-6">
            <h2 className="mb-4 font-display text-sm font-semibold">
              Why this was flagged
            </h2>
            {result ? (
              <ul className="flex flex-col gap-4">
                {result.reasons.map((r, i) => (
                  <li key={i} className="flex gap-3">
                    <div className="mt-0.5">
                      {r.weight > 25 ? (
                        <AlertTriangle size={16} className="text-[#f5a623]" />
                      ) : (
                        <CheckCircle2 size={16} className="text-[#8b93a3]" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-[#edeff3]">
                          {r.label}
                        </span>
                        <span className="font-mono text-xs text-[#8b93a3]">
                          {r.weight}%
                        </span>
                      </div>
                      <p className="mt-0.5 text-xs leading-relaxed text-[#8b93a3]">
                        {r.detail}
                      </p>
                      <div className="mt-1.5 h-1 w-full overflow-hidden rounded-full bg-[#1f2530]">
                        <div
                          className="h-full rounded-full bg-[#6c8cff]"
                          style={{ width: `${r.weight * 2.5}%` }}
                        />
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-[#8b93a3]">
                Explainability signals (pitch, spectral artifacts, context) will
                appear here after analysis.
              </p>
            )}
          </section>
        </div>
      </div>

      <footer className="mt-10 text-center text-xs text-[#8b93a3]">
        Built for Smart India Hackathon · On-device inference &amp; minimal
        audio retention by design
      </footer>
    </div>
  );
}
