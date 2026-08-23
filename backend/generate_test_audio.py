
import numpy as np
import soundfile as sf
import os

SR = 16000
DURATION = 6.0  # seconds


def _coarse_noise(rate_hz, std, n_coarse_min=8):
    """Random noise generated at a coarse rate (~frame rate) then interpolated
    to full sample rate, so it actually shows up as frame-to-frame variation
    (matches the ~30-60Hz frame resolution pitch/RMS trackers use) instead of
    averaging away like per-sample white noise would."""
    n_coarse = max(n_coarse_min, int(DURATION * rate_hz))
    coarse = np.random.normal(0, std, n_coarse)
    coarse_t = np.linspace(0, DURATION, n_coarse)
    full_t = np.linspace(0, DURATION, int(SR * DURATION), endpoint=False)
    return np.interp(full_t, coarse_t, coarse)


def make_natural_like():
    t = np.linspace(0, DURATION, int(SR * DURATION), endpoint=False)

    # Base pitch with slow vibrato + real frame-to-frame jitter
    base_f0 = 150 + 25 * np.sin(2 * np.pi * 0.6 * t)  # intonation contour
    jitter = _coarse_noise(rate_hz=35, std=14)  # coherent per-frame pitch jitter
    f0 = base_f0 + jitter
    phase = 2 * np.pi * np.cumsum(f0) / SR

    # Harmonics with uneven, drifting amplitudes (natural timbre)
    signal = np.zeros_like(t)
    for h, amp in enumerate([1.0, 0.55, 0.35, 0.22, 0.15, 0.10, 0.06], start=1):
        wobble = 1 + 0.05 * np.sin(2 * np.pi * (0.8 + 0.1 * h) * t + h)
        signal += amp * wobble * np.sin(h * phase)

    # Amplitude envelope with real shimmer (coarse-rate loudness jitter) + syllable pattern
    syllable_rate = 3.2
    envelope = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * syllable_rate * t))
    shimmer_noise = _coarse_noise(rate_hz=30, std=0.35)
    envelope = envelope * (1 + shimmer_noise)
    envelope = np.clip(envelope, 0.05, None)

    signal *= envelope

    # Add broadband natural-ish noise (breath/room noise, real high-freq content)
    noise = np.random.normal(0, 0.05, size=t.shape)
    signal += noise

    signal = signal / (np.max(np.abs(signal)) + 1e-6) * 0.8
    return signal.astype(np.float32)


def make_cloned_like():
    t = np.linspace(0, DURATION, int(SR * DURATION), endpoint=False)

    # Very smooth, stable pitch contour (minimal jitter) - typical vocoder trait
    base_f0 = 150 + 8 * np.sin(2 * np.pi * 0.3 * t)  # gentle, very regular contour
    f0 = base_f0  # no random jitter added
    phase = 2 * np.pi * np.cumsum(f0) / SR

    # Clean harmonics, smoothly decaying, very little variation
    signal = np.zeros_like(t)
    for h, amp in enumerate([1.0, 0.5, 0.28, 0.14, 0.06, 0.02, 0.005], start=1):
        signal += amp * np.sin(h * phase)

    # Very smooth, low-shimmer amplitude envelope
    syllable_rate = 3.0
    envelope = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * syllable_rate * t))
    # negligible shimmer noise
    signal *= envelope

    # Low-pass style smoothing (suppress high-frequency energy) to mimic
    # vocoder smoothing artifacts, and near-zero broadband noise floor
    kernel = np.ones(9) / 9
    signal = np.convolve(signal, kernel, mode="same")

    signal = signal / (np.max(np.abs(signal)) + 1e-6) * 0.8
    return signal.astype(np.float32)


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "test_audio")
    os.makedirs(out_dir, exist_ok=True)

    real_like = make_natural_like()
    cloned_like = make_cloned_like()

    sf.write(os.path.join(out_dir, "sample_real_like.wav"), real_like, SR)
    sf.write(os.path.join(out_dir, "sample_cloned_like.wav"), cloned_like, SR)

    print("Written:")
    print(" -", os.path.join(out_dir, "sample_real_like.wav"))
    print(" -", os.path.join(out_dir, "sample_cloned_like.wav"))
