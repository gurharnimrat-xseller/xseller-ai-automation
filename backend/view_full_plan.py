"""
View the complete plan organized by milestone
"""
import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

client = Client(auth=os.getenv("NOTION_API_KEY"))
db_id = os.getenv("NOTION_DATABASE_ID")

# Query all entries, sorted by EOD Date
results = client.databases.query(
    database_id=db_id,
    sorts=[{"property": "EOD Date", "direction": "ascending"}],
    page_size=100
)

# Organize by milestone
milestones = {
    "M0: Cloud Setup": [],
    "M1: Content": [],
    "M2: Media": [],
    "M3: Video": [],
    "M4: Review": [],
    "M5: Publishing": []
}

for page in results.get('results', []):
    props = page.get('properties', {})

    title_list = props.get('Item', {}).get('title', [])
    title = title_list[0].get('plain_text', 'No title') if title_list else 'No title'

    milestone_obj = props.get('Milestone', {}).get('select')
    milestone = milestone_obj.get('name', 'Unknown') if milestone_obj else 'Unknown'

    status_obj = props.get('Status', {}).get('status')
    status = status_obj.get('name', 'Unknown') if status_obj else 'Unknown'

    owner_list = props.get('Owner', {}).get('rich_text', [])
    owner = owner_list[0].get('plain_text', 'Unknown') if owner_list else 'Unknown'

    entry_type_obj = props.get('Entry Type', {}).get('select')
    entry_type = entry_type_obj.get('name', 'Unknown') if entry_type_obj else 'Unknown'

    eod_date = props.get('EOD Date', {}).get('date', {})

    summary_list = props.get('Summary / Notes', {}).get('rich_text', [])
    summary = summary_list[0].get('plain_text', '') if summary_list else ''

    entry = {
        'title': title,
        'status': status,
        'owner': owner,
        'type': entry_type,
        'date': eod_date.get('start', 'N/A') if eod_date else 'N/A',
        'summary': summary[:200] + '...' if len(summary) > 200 else summary
    }

    if milestone in milestones:
        milestones[milestone].append(entry)

# Print organized view
print("=" * 100)
print("🎯 XSELLER.AI DEVELOPMENT PLAN - NOTION DATABASE VIEW")
print("=" * 100)

for milestone, entries in milestones.items():
    if entries:
        print(f"\n{'='*100}")
        print(f"📋 {milestone}")
        print(f"{'='*100}")

        for i, entry in enumerate(entries, 1):
            status_emoji = {
                'Done': '✅',
                'In progress': '🔄',
                'Todo': '⚪',
                'Blocked': '🔴'
            }.get(entry['status'], '❓')

            print(f"\n{i}. {status_emoji} {entry['title']}")
            print(f"   Type: {entry['type']} | Owner: {entry['owner']} | Status: {entry['status']}")
            print(f"   Date: {entry['date']}")
            if entry['summary']:
                # Show first 2 lines of summary
                lines = entry['summary'].split('\n')[:3]
                for line in lines:
                    if line.strip():
                        print(f"   → {line.strip()}")

print("\n" + "=" * 100)
print(f"📊 TOTAL ENTRIES: {sum(len(entries) for entries in milestones.values())}")
print("=" * 100)
print(f"\n🔗 View in Notion: https://notion.so/{db_id.replace('-', '')}")
print("\n✅ Complete development plan is now in Notion!")
print("📝 You can now discuss and track progress on each task in Notion")
print("🚀 Tomorrow: Start M1A (News Scraper)")
