import datetime
import json
import os
import subprocess
from zoneinfo import ZoneInfo

LABEL = os.getenv("MONITOR_ISSUE_LABEL", "report:daily")
WINDOW = os.getenv("MONITOR_NZT_WINDOW", "05:00-10:00")
TZ = ZoneInfo("Pacific/Auckland")
STATE_PATH = "docs/MONITOR_STATE.json"


def run(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except Exception:
        return ""


def main() -> int:
    now = datetime.datetime.now(TZ)
    start_str, end_str = [part.strip() for part in WINDOW.split("-")]
    start_t = datetime.time.fromisoformat(start_str if ":" in start_str else f"{start_str}:00")
    end_t = datetime.time.fromisoformat(end_str if ":" in end_str else f"{end_str}:00")

    last = {}
    if os.path.exists(STATE_PATH):
        try:
            last = json.load(open(STATE_PATH))
        except Exception:
            last = {}

    today_key = now.date().isoformat()
    if not (start_t <= now.time() <= end_t):
        print("Outside NZT window, skipping.")
        return 0
    if last.get("posted_day") == today_key:
        print("Already posted today, skipping.")
        return 0

    open_prs = run(
        "gh pr list --json number,title,url,state --jq '.[] | \"- [#\\(.number)](\\(.url))  \\(.title)\"'"
    ) or "- none"
    failing = run(
        "gh run list --status failure --json databaseId,name,url --limit 5 --jq '.[] | \"- [\\(.name)](\\(.url))\"'"
    ) or "- none"
    budget = os.getenv("BUDGET_NZD_MONTHLY", "20")
    last_offload = "(none)"
    try:
        meta = json.load(open("docs/LAST_OFFLOAD.json"))
        last_offload = f"{meta.get('timestamp_utc','?')} — `{meta.get('request_id','?')}`"
    except Exception:
        pass

    body = f"""Daily Summary — {today_key} (NZT)

**Open PRs**
{open_prs}

**Failing checks**
{failing}

**Last offload**
{last_offload}

**Budget (NZD/mo)**
Cap: {budget} — Action on breach: Pause offloads

**Next 3 priorities**
1) Land offload/guardrails PR
2) Wire router into all generators
3) Monitor budget & Codespace hours
"""

    issue_search = run(
        f'gh issue list --label "{LABEL}" --search "Daily Summary — {today_key}" --json number --jq ".[0].number"'
    )
    if issue_search:
        subprocess.run(["gh", "issue", "comment", issue_search, "-b", body], check=False)
    else:
        subprocess.run(
            ["gh", "issue", "create", "-t", f"Daily Summary — {today_key} (NZT)", "-b", body, "-l", LABEL],
            check=False,
        )

    os.makedirs("docs", exist_ok=True)
    json.dump({"posted_day": today_key}, open(STATE_PATH, "w"))
    print("Monitor posted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
