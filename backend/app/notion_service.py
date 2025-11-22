"""
Notion Integration Service
Automatically posts daily updates to Notion database
"""
from __future__ import annotations

# from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401

import os
from datetime import datetime
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class NotionService:
    def __init__(self):
        self.api_key = os.getenv("NOTION_API_KEY")
        self.database_id = os.getenv("NOTION_DATABASE_ID", "3b5e99f3b35c45d58be175049977540a")

        if not self.api_key:
            raise ValueError("NOTION_API_KEY not set in environment")

        self.client = Client(auth=self.api_key)

    def post_daily_update(self, title, summary, owner="Claude", milestone="M0: Cloud Setup", status="Done"):
        """
        Post a daily update to Notion Work Log database

        Args:
            title: Update title
            summary: Update content (markdown supported)
            owner: Person responsible (Claude, Codex, Gurvinder)
            milestone: Milestone tag (M0: Cloud Setup, M1: Content, etc.)
            status: Task status (Todo, In progress, Blocked, Done)
        """
        try:
            # Create new page in database
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties={
                    "Item": {
                        "title": [
                            {
                                "text": {
                                    "content": title
                                }
                            }
                        ]
                    },
                    "Entry Type": {
                        "select": {
                            "name": "Daily update"
                        }
                    },
                    "Owner": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": owner
                                }
                            }
                        ]
                    },
                    "Status": {
                        "status": {
                            "name": status
                        }
                    },
                    "Milestone": {
                        "select": {
                            "name": milestone
                        }
                    },
                    "EOD Date": {
                        "date": {
                            "start": datetime.now().isoformat()
                        }
                    },
                    "Summary / Notes": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": summary[:2000]  # Notion has 2000 char limit for rich_text
                                }
                            }
                        ]
                    }
                }
            )

            print(f"✅ Posted to Notion: {title}")
            return response

        except Exception as e:
            print(f"❌ Failed to post to Notion: {str(e)}")
            raise

    def post_milestone_complete(self, milestone_num, title, summary, achievements):
        """
        Post milestone completion to Notion

        Args:
            milestone_num: Milestone number (0, 1, 2, etc.)
            title: Milestone title
            summary: Summary text
            achievements: List of achievement strings
        """
        # Format achievements as bullet points
        formatted_summary = f"{summary}\n\n✅ Achievements:\n"
        for achievement in achievements:
            formatted_summary += f"• {achievement}\n"

        # Map milestone numbers to full names
        milestone_names = {
            0: "M0: Cloud Setup",
            1: "M1: Content",
            2: "M2: Media",
            3: "M3: Video",
            4: "M4: Review",
            5: "M5: Publishing"
        }

        return self.post_daily_update(
            title=f"Milestone {milestone_num}: {title} ✅",
            summary=formatted_summary,
            owner="Claude + Codex",
            milestone=milestone_names.get(milestone_num, f"M{milestone_num}"),
            status="Done"
        )

    def test_connection(self):
        """Test Notion API connection"""
        try:
            # Try to retrieve database info
            database = self.client.databases.retrieve(database_id=self.database_id)
            print(f"✅ Connected to Notion database: {database.get('title', [{}])[0].get('plain_text', 'Unknown')}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Notion: {str(e)}")
            return False


# Quick test function
if __name__ == "__main__":
    service = NotionService()

    # Test connection
    if service.test_connection():
        print("\n✅ Notion integration working!")

        # Post test update
        service.post_daily_update(
            title="November 10, 2025 - Milestone 0 Complete ✅",
            summary="""✅ MILESTONE 0 COMPLETE!

Today's Achievements:
- Migrated 66 files (12,401 lines) to GitHub
- Removed exposed API keys (security fix)
- Created Pull Request #3 (merged)
- Codespace environment ready
- MacBook dependency eliminated!

Technical Setup Complete:
- GitHub Actions CI/CD
- Docker container with Python 3.11 + Node 20
- FFmpeg, OpenCV, Whisper installed
- Competitor analysis done by Codex
- Notion integration working! 🎉

Next Steps:
- Tomorrow: Start Milestone 1 (News Scraper)
- Codex works in Codespace
- Daily updates posted here automatically

Your laptop is now FREE! 🎉

---
Link to PR: https://github.com/gurharnimrat-xseller/xseller-ai-automation/pull/3
Commit: a114c0e
Files: 66 changed
Lines: +12,401 / -1,086""",
            owner="Claude",
            milestone="M0: Cloud Setup",
            status="Done"
        )
    else:
        print("\n❌ Check your Notion API key and database ID")
