"""
Quick test script to verify content scraping works
"""
import asyncio
import sys
import os

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(__file__))

from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401, E402
from app import content_scraper  # noqa: E402


async def main():
    print("="*80)
    print("🧪 TESTING CONTENT SCRAPER")
    print("="*80)

    try:
        # Test fetching content
        articles = await content_scraper.fetch_all_content()

        print(f"\n✅ SUCCESS! Fetched {len(articles)} articles\n")

        # Display top 5 articles
        print("Top 5 Articles:")
        print("-" * 80)
        for i, article in enumerate(articles[:5], 1):
            print(f"\n{i}. {article.get('title', 'No title')}")
            print(f"   Source: {article.get('source', 'Unknown')}")
            print(f"   URL: {article.get('url', 'No URL')}")
            print(f"   Published: {article.get('published', 'Unknown')}")
            print(f"   Summary: {article.get('summary', '')[:150]}...")

        print("\n" + "="*80)
        print("✅ Content scraping is working!")
        print("="*80)

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
