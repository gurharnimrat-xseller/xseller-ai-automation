"""
Test script for the new video generation system
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401, E402
from app import video_production  # noqa: E402


async def main():
    print("="*80)
    print("🎬 TESTING PROFESSIONAL VIDEO GENERATION")
    print("="*80)

    # Test script with proper timing
    test_script = """Hook (0-3s): Did you know 90% of AI startups fail in year one?

Main (4-12s): But the 10% that survive do three things differently. First, they ship fast and iterate daily. Second, they listen obsessively to users. Third, they focus on solving ONE problem really well.

Why (13-17s): This isn't luck. It's a proven playbook that separates winners from losers in the AI revolution.

CTA (18-20s): Want to learn the full framework? Follow for daily startup insights."""

    print("\n📝 Test Script:")
    print("-" * 80)
    print(test_script)
    print("-" * 80)

    # Generate video
    print("\n🎬 Starting video generation...")
    result = await video_production.generate_video_from_script(
        script=test_script,
        title="AI Startup Success Formula"
    )

    print("\n" + "="*80)
    if result.get("success"):
        print("✅ VIDEO GENERATION SUCCESSFUL!")
        print("="*80)
        print(f"Video Path: {result['video_path']}")
        print(f"Duration: {result.get('duration', 0)}s")
        print(f"Scenes: {result.get('scenes', 0)}")
        print("\nYou can now view the video at the path above!")
    else:
        print("❌ VIDEO GENERATION FAILED")
        print("="*80)
        print(f"Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    asyncio.run(main())
