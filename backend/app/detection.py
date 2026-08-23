"""
detection.py
-------------
Core voice-authenticity detection engine.

APPROACH: We use classic digital-signal-processing features that research
literature consistently associates with synthetic / cloned speech, rather
than a heavy pretrained deep-learning checkpoint. This keeps the system:
  - fast (runs on CPU, no GPU needed)
  - fully offline after install (no flaky model downloads at hackathon WiFi)
  - explainable (every feature maps directly to a human-readable reason,
    which powers the "Why this was flagged" panel in the frontend)

Features used (all well-documented anti-spoofing indicators):
  1. Pitch (F0) jitter        -> natural voices have micro-irregular pitch;
                                  many TTS/vocoders produce unnaturally smooth F0.
  2. Shimmer (amplitude jitter)-> natural amplitude micro-variation is higher
                                  in genuine speech than in vocoder output.
  3. Spectral flatness         -> synthetic speech from neural vocoders often
                                  shows different (typically smoother) spectral
                                  flatness patterns than natural speech.
  4. High-frequency spectral energy ratio -> vocoder artifacts often show up
                                  as unusual energy distribution above 4kHz.
  5. Zero-crossing rate variance -> natural speech has more micro-variation.

This is intentionally a lightweight, interpretable MVP layer. In a full
production system this would sit alongside (or be replaced by) a trained
neural countermeasure model (e.g. AASIST / RawNet2 on ASVspoof) -- the
API contract below is designed so that swap is a drop-in replacement.
"""

import numpy as np
import librosa


CHUNK_SECONDS = 2.0


def _safe_div(a, b, default=0.0):
    return a / b if b not in (0, 0.0) else default


def _extract_chunk_features(y: np.ndarray, sr: int) -> dict:
    """Extract interpretable DSP features from a short audio chunk."""
    if len(y) < sr * 0.2:  # too short to analyze meaningfully
        return None

    # --- Pitch (F0) tracking ---
    f0, voiced_flag, _ = librosa.pyin(
        y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"), sr=sr
    )
    voiced_f0 = f0[voiced_flag] if voiced_flag is not None else np.array([])
    voiced_f0 = voiced_f0[~np.isnan(voiced_f0)]

    if len(voiced_f0) > 3:
        f0_diffs = np.abs(np.diff(voiced_f0))
        jitter = _safe_div(np.mean(f0_diffs), np.mean(voiced_f0))
    else:
        jitter = None  # unvoiced/silent chunk

    # --- Amplitude (shimmer proxy) ---
    rms = librosa.feature.rms(y=y)[0]
    shimmer = _safe_div(np.std(rms), np.mean(rms))

    # --- Spectral flatness ---
    flatness = float(np.mean(librosa.feature.spectral_flatness(y=y)))

    # --- High-frequency energy ratio ---
    S = np.abs(librosa.stft(y))
    freqs = librosa.fft_frequencies(sr=sr)
    hf_mask = freqs > 4000
    hf_ratio = _safe_div(np.sum(S[hf_mask, :]), np.sum(S))

    # --- Zero crossing rate variance ---
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    zcr_var = float(np.var(zcr))

    return {
        "jitter": jitter,
        "shimmer": shimmer,
        "flatness": flatness,
        "hf_ratio": hf_ratio,
        "zcr_var": zcr_var,
    }


def _chunk_score(feats: dict) -> float:
    """
    Map raw DSP features to a 0-100 synthetic-likelihood score.
    Thresholds are heuristic, calibrated against the bundled test samples.
    Lower jitter/shimmer/zcr-variance and unusual flatness/hf-ratio push
    the score UP (more likely synthetic).
    """
    if feats is None:
        return 20.0  # neutral-low for silence/too-short chunk

    score = 30.0  # baseline

    # Jitter: natural speech has frame-to-frame pitch micro-variation;
    # very low jitter suggests an overly-regular, machine-generated F0 contour.
    if feats["jitter"] is not None:
        if feats["jitter"] < 0.008:
            score += 28
        elif feats["jitter"] < 0.02:
            score += 12
        else:
            score -= 8

    # Shimmer: very low amplitude variance -> unnaturally smooth loudness
    if feats["shimmer"] < 0.10:
        score += 18
    elif feats["shimmer"] < 0.15:
        score += 6
    else:
        score -= 6

    # Spectral flatness: neural vocoder output is often "too clean"
    if feats["flatness"] < 0.001:
        score += 12
    elif feats["flatness"] > 0.08:
        score += 8  # overly noisy/flat can also indicate artifacts

    # High-frequency energy ratio: unusually low HF content -> smoothing artifact
    if feats["hf_ratio"] < 0.02:
        score += 14

    # Zero-crossing-rate variance: very low variance -> monotone/synthetic texture
    if feats["zcr_var"] < 0.00001:
        score += 10

    return float(max(2, min(98, score)))


def analyze_audio(path: str) -> dict:
    """
    Run chunk-wise + overall analysis on an audio file.
    Returns a dict matching the frontend's AnalysisResult shape.
    """
    y, sr = librosa.load(path, sr=16000, mono=True)
    duration = len(y) / sr
    chunk_len = int(CHUNK_SECONDS * sr)

    chunks = []
    all_feats = []
    for i, start in enumerate(range(0, len(y), chunk_len)):
        chunk = y[start : start + chunk_len]
        if len(chunk) < sr * 0.3:
            continue
        feats = _extract_chunk_features(chunk, sr)
        score = _chunk_score(feats)
        chunks.append(
            {
                "startSec": round(i * CHUNK_SECONDS, 1),
                "endSec": round(min((i + 1) * CHUNK_SECONDS, duration), 1),
                "score": round(score, 1),
            }
        )
        if feats is not None:
            all_feats.append(feats)

    if not chunks:
        chunks = [{"startSec": 0, "endSec": round(duration, 1), "score": 20.0}]

    overall_score = round(float(np.mean([c["score"] for c in chunks])), 1)

    # Build explainability reasons from averaged features
    reasons = []
    if all_feats:
        avg_jitter = np.nanmean([f["jitter"] for f in all_feats if f["jitter"] is not None] or [np.nan])
        avg_shimmer = np.mean([f["shimmer"] for f in all_feats])
        avg_flatness = np.mean([f["flatness"] for f in all_feats])
        avg_hf = np.mean([f["hf_ratio"] for f in all_feats])

        if not np.isnan(avg_jitter) and avg_jitter < 0.02:
            reasons.append(
                {
                    "label": "Unnaturally smooth pitch (low jitter)",
                    "detail": f"Average pitch jitter {avg_jitter:.4f} is below the natural-speech range (~0.02-0.08), suggesting synthetic F0 generation.",
                    "weight": 32,
                }
            )
        if avg_shimmer < 0.15:
            reasons.append(
                {
                    "label": "Low amplitude micro-variation (shimmer)",
                    "detail": f"Shimmer proxy {avg_shimmer:.3f} indicates unusually stable loudness, typical of vocoder-generated audio.",
                    "weight": 26,
                }
            )
        if avg_hf < 0.02:
            reasons.append(
                {
                    "label": "Suppressed high-frequency energy",
                    "detail": f"Only {avg_hf*100:.1f}% of spectral energy lies above 4kHz, consistent with neural vocoder smoothing artifacts.",
                    "weight": 24,
                }
            )
        if avg_flatness < 0.001:
            reasons.append(
                {
                    "label": "Overly clean spectral texture",
                    "detail": f"Spectral flatness {avg_flatness:.4f} is lower than typical natural recordings, indicating an unusually 'clean' synthesis signature.",
                    "weight": 18,
                }
            )

    if not reasons:
        reasons.append(
            {
                "label": "Natural prosody and spectral variation",
                "detail": "Pitch jitter, shimmer, and spectral texture fall within the expected range for genuine human speech.",
                "weight": 10,
            }
        )

    band = "risk" if overall_score >= 70 else ("warning" if overall_score >= 40 else "safe")

    return {
        "riskScore": overall_score,
        "band": band,
        "chunks": chunks,
        "reasons": reasons,
        "durationSec": round(duration, 2),
    }
