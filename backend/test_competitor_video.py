"""
Test EXACT Competitor-Style Video Generation
Matches viral tech shorts (30 seconds, 5-scene structure)
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import video_competitor_exact


async def main():
    print("="*80)
    print("🎬 TESTING COMPETITOR-EXACT VIDEO GENERATION")
    print("="*80)

    # Real-world example: GPT-4 Vision announcement
    test_script = """Hook: Can AI actually see and understand images now?

Demo: OpenAI just released GPT-4 Vision API - and it's insane. Upload any image and get detailed analysis in seconds.

Proof: 95% accuracy rate. 10X faster than competitors. Handles charts, diagrams, even memes.

Impact: This changes everything for developers, designers, and content creators. No more manual image tagging.

CTA: Link in bio for full tutorial. Follow @yourhandle for daily AI updates!"""

    title = "GPT-4 Vision API Released"

    print(f"\n📝 Title: {title}")
    print("\n📄 Script:")
    print("-" * 80)
    print(test_script)
    print("-" * 80)

    print("\n🎬 Generating 30-second competitor-style video...")
    print("   Structure: Hook (3s) → Demo (6s) → Proof (9s) → Impact (6s) → CTA (6s)")
    print("   Features:")
    print("   ✅ Exact text styles (90pt/50pt/colors)")
    print("   ✅ Relevant stock footage (Pexels)")
    print("   ✅ AI voiceover (Eleven Labs)")
    print("   ✅ Professional transitions")
    print("\nThis will take 2-3 minutes...\n")

    # Generate video
    result = await video_competitor_exact.generate_exact_competitor_video(
        script=test_script,
        title=title,
        add_voiceover=True
    )

    print("\n" + "="*80)
    if result.get("success"):
        print("✅ VIDEO GENERATION SUCCESSFUL!")
        print("="*80)
        print(f"📍 Video Location: {result['video_path']}")
        print(f"⏱️  Duration: {result['duration']} seconds")
        print(f"🎬 Structure: {result.get('structure', 'Hook/Demo/Proof/Impact/CTA')}")
        print("🎞️  Scenes: 5 (rapid-fire tech shorts style)")
        print("\n💡 Next Steps:")
        print("   1. Open the video file to review")
        print("   2. Test on actual social media (YouTube Shorts/TikTok/Instagram)")
        print("   3. Adjust script for better engagement")
        print("   4. Scale to full automation!")
        print("="*80)
    else:
        print("❌ VIDEO GENERATION FAILED")
        print("="*80)
        print(f"Error: {result.get('error', 'Unknown error')}")
        print("\nTroubleshooting:")
        print("   - Check that MoviePy is installed: pip install moviepy")
        print("   - Verify API keys in .env file")
        print("   - Check backend/output/videos/ folder permissions")


if __name__ == "__main__":
    asyncio.run(main())
