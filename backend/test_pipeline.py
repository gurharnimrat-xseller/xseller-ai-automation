"""
Test the entire content generation pipeline:
1. Scrape content
2. Generate viral text posts
3. Generate viral video scripts
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import content_scraper
from app import script_generator


async def main():
    print("="*80)
    print("🧪 TESTING COMPLETE CONTENT GENERATION PIPELINE")
    print("="*80)

    try:
        # Step 1: Scrape content
        print("\n📰 STEP 1: Scraping content...")
        print("-" * 80)
        articles = await content_scraper.fetch_all_content()
        print(f"✅ Fetched {len(articles)} articles\n")

        if not articles:
            print("❌ No articles fetched. Exiting.")
            return

        # Use top article for testing
        top_article = articles[0]
        print(f"📝 Testing with article: {top_article.get('title', 'No title')[:80]}...")
        print(f"   Source: {top_article.get('source', 'Unknown')}")
        print()

        # Step 2: Generate viral text posts
        print("\n✍️  STEP 2: Generating viral text posts...")
        print("-" * 80)
        text_posts = await script_generator.generate_viral_text_posts(
            article=top_article,
            num_variants=3,
            platforms=["LinkedIn", "Twitter", "Instagram"]
        )

        print(f"✅ Generated {len(text_posts)} text posts\n")
        for i, post in enumerate(text_posts, 1):
            platform = post.get('platform', 'Unknown')
            text = post.get('text', '')
            hook_type = post.get('hook_type', 'unknown')
            framework = post.get('framework', 'unknown')

            print(f"Post {i} - {platform} [{hook_type}/{framework}]:")
            print(f"{text[:200]}...")
            print()

        # Step 3: Generate viral video scripts
        print("\n🎬 STEP 3: Generating viral video scripts...")
        print("-" * 80)
        video_scripts = await script_generator.generate_viral_video_scripts(
            article=top_article,
            num_variants=2,
            duration=20
        )

        print(f"✅ Generated {len(video_scripts)} video scripts\n")
        for i, script_data in enumerate(video_scripts, 1):
            script = script_data.get('script', '')
            hook_type = script_data.get('hook_type', 'unknown')
            formula = script_data.get('formula', 'unknown')
            duration = script_data.get('duration', 0)

            print(f"Script {i} - {duration}s [{hook_type}/{formula}]:")
            print(f"{script[:300]}...")
            print()

        # Summary
        print("="*80)
        print("✅ PIPELINE TEST COMPLETE!")
        print("="*80)
        print(f"Articles Scraped: {len(articles)}")
        print(f"Text Posts Generated: {len(text_posts)}")
        print(f"Video Scripts Generated: {len(video_scripts)}")
        print("="*80)

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY environment variable not set")
        print("Please set it: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)

    asyncio.run(main())
