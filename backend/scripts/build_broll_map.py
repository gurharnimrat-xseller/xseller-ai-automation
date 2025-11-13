from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401
import csv
import re
from pathlib import Path

FRAMES_DIR = Path("backend/output/competitor_analysis/frames")
SCENE_FILE = Path("backend/output/competitor_analysis/scene_changes.txt")
OUTPUT_CSV = Path("backend/output/competitor_analysis/broll_sync_map.csv")

SCENE_REGEX = re.compile(r"pkt_pts_time=(\d+\.?\d*)")


def parse_scene_changes():
    times = []
    if not SCENE_FILE.exists():
        return times
    for line in SCENE_FILE.read_text().splitlines():
        match = SCENE_REGEX.search(line)
        if match:
            times.append(float(match.group(1)))
    return times


def build_rows(scene_times):
    rows = []
    frame_paths = sorted(FRAMES_DIR.glob("frame_*.jpg"))
    for frame_path in frame_paths:
        timestamp = int(frame_path.stem.split("_")[-1])
        rows.append(
            {
                "timestamp_s": timestamp,
                "frame_file": frame_path.name,
                "is_scene_change": any(abs(timestamp - t) < 0.5 for t in scene_times),
                "notes": "",
            }
        )
    return rows


def main():
    scene_times = parse_scene_changes()
    rows = build_rows(scene_times)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp_s", "frame_file", "is_scene_change", "notes"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} entries to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
