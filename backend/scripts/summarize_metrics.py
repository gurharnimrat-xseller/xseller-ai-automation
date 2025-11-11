from agents.checks.router import should_offload, offload_to_gemini  # guardrails
import json
from pathlib import Path

OUTPUT_DIR = Path("backend/output/competitor_analysis")


def load_json(path: Path):
    if not path.exists():
        return {}
    return json.loads(path.read_text() or "{}")


def main():
    tech = load_json(OUTPUT_DIR / "technical_specs.json")
    voice = load_json(OUTPUT_DIR / "voice_profile.json")
    metrics = {
        "video": {},
        "audio": {},
        "voice": {},
    }

    for stream in tech.get("streams", []):
        if stream.get("codec_type") == "video":
            metrics["video"] = {
                "resolution": f"{stream.get('width')}x{stream.get('height')}",
                "fps": stream.get("avg_frame_rate"),
                "bitrate": stream.get("bit_rate"),
                "codec": stream.get("codec_name"),
            }
        if stream.get("codec_type") == "audio":
            metrics["audio"] = {
                "sample_rate": stream.get("sample_rate"),
                "channels": stream.get("channels"),
                "bitrate": stream.get("bit_rate"),
                "codec": stream.get("codec_name"),
            }

    metrics["voice"] = {
        "duration_seconds": voice.get("duration_seconds"),
        "words_per_minute": voice.get("words_per_minute"),
        "tempo_bpm": voice.get("tempo_bpm"),
        "mean_rms": voice.get("mean_rms"),
        "mean_pitch_hz": voice.get("mean_pitch_hz"),
    }

    (OUTPUT_DIR / "quality_benchmark.json").write_text(json.dumps(metrics, indent=2))
    print(f"Saved metrics to {OUTPUT_DIR / 'quality_benchmark.json'}")


if __name__ == "__main__":
    main()
