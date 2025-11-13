from agents.checks.router import (
    should_offload,
    offload_to_gemini,
)  # noqa: F401
import json
from pathlib import Path

import librosa
import numpy as np

BASE_DIR = (
    Path(__file__).resolve().parents[1] / "output" / "competitor_analysis"
)
AUDIO_PATH = BASE_DIR / "audio" / "narration.wav"
TRANSCRIPT_PATH = BASE_DIR / "transcript.txt"
REPORT_PATH = BASE_DIR / "voice_profile.json"


def load_audio(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found at {path}")
    signal, sr = librosa.load(path, sr=44100)
    return signal, sr


def compute_voice_metrics(signal: np.ndarray, sr: int) -> dict:
    duration = len(signal) / sr
    rms = librosa.feature.rms(y=signal)[0]
    rms_mean = float(np.mean(rms))
    rms_std = float(np.std(rms))

    tempo, _ = librosa.beat.beat_track(y=signal, sr=sr)

    pitches, magnitudes = librosa.piptrack(y=signal, sr=sr)
    pitch = pitches[magnitudes > np.median(magnitudes)]
    mean_pitch = float(np.mean(pitch)) if pitch.size else 0.0

    return {
        "duration_seconds": duration,
        "tempo_bpm": tempo,
        "mean_rms": rms_mean,
        "std_rms": rms_std,
        "mean_pitch_hz": mean_pitch,
    }


def estimate_words_per_minute(transcript: Path, duration: float) -> float:
    if not transcript.exists():
        return 0.0
    words = transcript.read_text().split()
    minutes = duration / 60 if duration else 1
    return len(words) / minutes


def main():
    signal, sr = load_audio(AUDIO_PATH)
    metrics = compute_voice_metrics(signal, sr)
    metrics["words_per_minute"] = estimate_words_per_minute(
        TRANSCRIPT_PATH, metrics["duration_seconds"]
    )

    serializable = {}
    for key, value in metrics.items():
        if isinstance(value, np.ndarray):
            serializable[key] = float(np.mean(value))
        elif isinstance(value, np.floating):
            serializable[key] = float(value)
        else:
            serializable[key] = value
    REPORT_PATH.write_text(json.dumps(serializable, indent=2))
    print(f"Voice profile saved to {REPORT_PATH}")


if __name__ == "__main__":
    main()
