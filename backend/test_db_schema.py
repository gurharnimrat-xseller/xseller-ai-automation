"""
Quick script to check database schema
"""
from __future__ import annotations

from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401

import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

client = Client(auth=os.getenv("NOTION_API_KEY"))
db_id = "234d0b5e53e44eacaa73d1d3f784ab11"

try:
    # Get database schema
    database = client.databases.retrieve(database_id=db_id)

    print(f"✅ Database: {database.get('title', [{}])[0].get('plain_text', 'Unknown')}")
    print("\n📋 Properties:")

    for prop_name, prop_info in database.get('properties', {}).items():
        prop_type = prop_info.get('type')
        print(f"  • {prop_name}: {prop_type}")

        # Show select options if available
        if prop_type == 'select' and 'select' in prop_info:
            options = prop_info['select'].get('options', [])
            if options:
                print(f"    Options: {', '.join([opt['name'] for opt in options])}")

        # Show status options if available
        if prop_type == 'status' and 'status' in prop_info:
            options = prop_info['status'].get('options', [])
            if options:
                print(f"    Options: {', '.join([opt['name'] for opt in options])}")

except Exception as e:
    print(f"❌ Error: {str(e)}")
