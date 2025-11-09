# Codespaces Environment for Video Analysis

Use this guide to launch the heavier competitor-analysis workflow inside GitHub Codespaces so your local 2017 MacBook stays cool.

## 1. Prerequisites

- GitHub account with access to this repo.
- Codespaces enabled for the organization.
- Optional: GitHub Pro (gives 60 free Codespaces hours/month).

## 2. Launch a Codespace

1. Push these `.devcontainer` files to the default branch if they are not there already.
2. On GitHub, click **Code → Codespaces → Create codespace on main** (or relevant branch).
3. The devcontainer will build automatically (~5–7 minutes on first run).

## 3. What the Devcontainer Includes

- Ubuntu base with Python 3.11, Node 20, git, ffmpeg, OpenCV, Whisper, yt-dlp, MoviePy, Librosa, Pandas, etc.
- VS Code extensions for Python, Jupyter, Copilot, and Prettier.
- Ports 3000/8000 pre-forwarded for frontend/backend previews.

## 4. Running the Competitor Analysis

Inside the Codespace terminal (repo root):

```bash
cd backend
python scripts/analyze_competitor.py
```

> _Use whichever script/notebook we add for analysis; the environment already has all dependencies._

Artifacts will appear under `backend/output/competitor_analysis/` and automatically sync back to the repo so you can review locally.

## 5. Tips

- Pause the Codespace when not in use to save hours.
- If you need more CPU/RAM, bump the Codespace machine type from the command palette (`Codespaces: Change Machine Type`).
- Keep long-running ffmpeg/whisper jobs inside screen/tmux if you expect >1 hour runs, or run them via GitHub Actions with the same container.
