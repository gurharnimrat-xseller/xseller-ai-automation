"""
Quick script to query recent entries from Notion
"""
from agents.checks.router import should_offload, offload_to_gemini  # guardrails
import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

client = Client(auth=os.getenv("NOTION_API_KEY"))
db_id = "234d0b5e53e44eacaa73d1d3f784ab11"

try:
    # Query recent entries
    results = client.databases.query(
        database_id=db_id,
        sorts=[
            {
                "property": "EOD Date",
                "direction": "descending"
            }
        ],
        page_size=5
    )

    print(f"✅ Recent entries in database:\n")
    for page in results.get('results', []):
        title = page.get('properties', {}).get('Item', {}).get('title', [{}])[0].get('plain_text', 'No title')
        eod_date = page.get('properties', {}).get('EOD Date', {}).get('date', {})
        status = page.get('properties', {}).get('Status', {}).get('status', {}).get('name', 'Unknown')
        owner = page.get('properties', {}).get('Owner', {}).get('rich_text', [{}])[0].get('plain_text', 'Unknown')

        print(f"  📝 {title}")
        print(f"     Status: {status}")
        print(f"     Owner: {owner}")
        if eod_date:
            print(f"     Date: {eod_date.get('start', 'N/A')}")
        print()

except Exception as e:
    print(f"❌ Error: {str(e)}")
