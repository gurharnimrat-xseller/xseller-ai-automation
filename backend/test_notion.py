"""
Quick script to find database ID in Notion page
"""
import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

client = Client(auth=os.getenv("NOTION_API_KEY"))
page_id = "3b5e99f3b35c45d58be175049977540a"

try:
    # Get the page
    page = client.pages.retrieve(page_id=page_id)
    print(f"✅ Found page: {page.get('properties', {}).get('title', {}).get('title', [{}])[0].get('plain_text', 'Unknown')}")

    # Get blocks on the page (this includes databases)
    blocks = client.blocks.children.list(block_id=page_id)

    print("\n📋 Blocks on page:")
    for block in blocks.get('results', []):
        block_type = block.get('type')
        block_id = block.get('id')

        if block_type == 'child_database':
            db_title = block.get('child_database', {}).get('title', 'Unnamed Database')
            print(f"  📊 Database found: {db_title}")
            print(f"     ID: {block_id}")
            print(f"     URL: https://www.notion.so/{block_id.replace('-', '')}")
        else:
            print(f"  • {block_type}: {block_id}")

    # Try to search for databases
    print("\n🔍 Searching for databases...")
    search_results = client.search(
        query="Work Log",
        filter={"property": "object", "value": "database"}
    )

    for result in search_results.get('results', []):
        if result.get('object') == 'database':
            title = result.get('title', [{}])[0].get('plain_text', 'Unknown')
            db_id = result.get('id')
            print(f"  📊 Found database: {title}")
            print(f"     ID: {db_id}")

except Exception as e:
    print(f"❌ Error: {str(e)}")
