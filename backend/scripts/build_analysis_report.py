from pathlib import Path

OUTPUT_DIR = Path("backend/output/competitor_analysis")


def load_text(name: str) -> str:
    path = OUTPUT_DIR / name
    return path.read_text() if path.exists() else ""


def main():
    transcript = load_text("transcript.txt")
    report_path = OUTPUT_DIR / "analysis_report.md"
    report = []
    report.append("# Competitor Video Analysis")
    report.append("")
    report.append("## Hook & Opening (0-3s)")
    report.append("- Identify the exact words used in the hook and note the visual in the first frame.")
    report.append("")
    report.append("## Narrative Structure")
    report.append("- Summarize how the video introduces the problem, provides value, and calls to action.")
    report.append("")
    report.append("## Visual Style & B-roll Timing")
    report.append("- Reference `broll_sync_map.csv` to describe shot changes and overlay usage.")
    report.append("")
    report.append("## Voice & Audio Characteristics")
    report.append("- Use `voice_profile.json` to comment on pacing, energy, and audio mix.")
    report.append("")
    report.append("## Key Takeaways")
    report.append("- What makes this video stop-worthy?")
    report.append("- How should xseller.ai emulate or differentiate?")
    report.append("")
    report.append("### Transcript Reference")
    report.append("```")
    report.append(transcript.strip())
    report.append("```")

    report_path.write_text("\n".join(report))
    print(f"Wrote analysis template to {report_path}")


if __name__ == "__main__":
    main()
