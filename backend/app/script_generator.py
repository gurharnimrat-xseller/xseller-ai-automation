"""
Viral Script Generator Module
Advanced script generation with proven hooks, formulas, and psychological triggers.
"""
from agents.checks.router import should_offload, offload_to_gemini  # guardrails

from __future__ import annotations

import json
import random
from typing import Any, Dict, List, Optional
# removed per guardrails; use router
# # removed per guardrails; use router
# # removed per guardrails; use router
# # removed per guardrails; use router import AsyncOpenAI
import os


# ==================== VIRAL HOOK FORMULAS ====================

VIRAL_HOOK_TEMPLATES = {
    "question": [
        "Did you know {fact}?",
        "What if I told you {fact}?",
        "Want to know why {outcome}?",
        "Ever wondered how {topic}?",
        "Why do {number}% of people {action}?",
    ],
    "shocking": [
        "This will change everything...",
        "You won't believe what just happened",
        "{number}% of experts got this wrong",
        "This {topic} breakthrough is going viral",
        "Nobody saw this coming...",
        "The {industry} world just changed forever",
    ],
    "curiosity_gap": [
        "The secret {experts} don't want you to know",
        "What {successful_people} do that others don't",
        "The one thing that makes {outcome} possible",
        "Here's what nobody tells you about {topic}",
        "The hidden truth about {topic}",
    ],
    "pattern_interrupt": [
        "Stop doing {bad_practice}. Start doing {good_practice}",
        "Forget everything you know about {topic}",
        "Everyone says {common_advice}. They're wrong",
        "Most people {bad_action}. Winners {good_action}",
    ],
    "story": [
        "I made a mistake that cost me {loss}...",
        "Last {timeframe}, I discovered {insight}",
        "This happened and it changed my perspective on {topic}",
        "A year ago, I {past_state}. Today, I {present_state}",
    ],
    "urgency": [
        "This is happening RIGHT NOW",
        "You have {timeframe} to {action}",
        "Don't miss this {opportunity}",
        "This changes today",
    ],
    "authority": [
        "{Expert_name} just revealed {insight}",
        "New study shows {finding}",
        "{Company} just announced {news}",
        "Top {role} shares {secret}",
    ],
}

PLATFORM_STRATEGIES = {
    "LinkedIn": {
        "tone": "professional, insightful, thought-leadership",
        "length": "150-250 words",
        "style": "value-driven, data-backed, career-focused",
        "cta": "Comment, share insights, tag colleagues",
    },
    "Twitter": {
        "tone": "punchy, direct, conversational",
        "length": "100-280 characters",
        "style": "thread-friendly, quotable, hot-take",
        "cta": "Retweet, reply with thoughts",
    },
    "Instagram": {
        "tone": "casual, visual, aspirational",
        "length": "80-150 words",
        "style": "storytelling, relatable, emoji-friendly",
        "cta": "Double-tap, save, share to stories",
    },
    "TikTok": {
        "tone": "energetic, authentic, trending",
        "length": "script for 15-60 seconds",
        "style": "hook-driven, fast-paced, entertainment-first",
        "cta": "Like, follow, duet",
    },
    "Facebook": {
        "tone": "friendly, community-oriented, conversational",
        "length": "100-200 words",
        "style": "discussion-starter, relatable, shareable",
        "cta": "Comment, share, react",
    },
    "YouTube Shorts": {
        "tone": "dynamic, educational, entertaining",
        "length": "script for 15-60 seconds",
        "style": "visual storytelling, value-packed, rewatchable",
        "cta": "Subscribe, like, watch next",
    },
}

# Copywriting frameworks
COPYWRITING_FRAMEWORKS = [
    "AIDA",  # Attention, Interest, Desire, Action
    "PAS",  # Problem, Agitate, Solution
    "PASTOR",  # Problem, Amplify, Story, Transformation, Offer, Response
    "FAB",  # Features, Advantages, Benefits
    "4Ps",  # Picture, Promise, Proof, Push
]


# ==================== SCRIPT GENERATION ====================

async def generate_viral_text_posts(
    article: Dict[str, Any],
    num_variants: int = 5,
    platforms: Optional[List[str]] = None
) -> List[Dict[str, str]]:
    """
    Generate viral text posts from an article using advanced hooks and frameworks.

    Args:
        article: Dict with title, summary, url, source
        num_variants: Number of variations to generate
        platforms: Target platforms (if None, generates for all)

    Returns:
        List of dicts with 'platform', 'text', 'hook_type' fields
    """
    client = AsyncOpenAI()

    if platforms is None:
        platforms = ["LinkedIn", "Twitter", "Instagram", "Facebook"]

    # Build enhanced prompt
    prompt = f"""You are an EXPERT viral social media copywriter. Your posts get 10x more engagement than average.

ARTICLE INFO:
Title: {article.get('title', '')}
Summary: {article.get('summary', '')}
Source: {article.get('source', '')}

TASK: Create {num_variants} HIGH-PERFORMING social media posts for: {', '.join(platforms)}

CRITICAL REQUIREMENTS:
1. START WITH A VIRAL HOOK (first 5-8 words) - use proven formulas:
   - Question Hook: "Did you know..." "What if..."
   - Shocking Statement: "This will change everything..." "X% of experts got this wrong"
   - Curiosity Gap: "The secret most people don't know..." "What winners do differently"
   - Pattern Interrupt: "Stop doing X. Start doing Y"
   - Story Hook: "I made a mistake that cost me..." "A year ago, I..."

2. PLATFORM OPTIMIZATION:
   - LinkedIn: Professional, thought-leadership, 150-250 words, data-backed
   - Twitter: Punchy, quotable, 100-280 chars, hot-take worthy
   - Instagram: Casual, visual, 80-150 words, emoji-friendly
   - Facebook: Friendly, discussion-starter, 100-200 words

3. PROVEN FRAMEWORKS:
   - Use AIDA (Attention, Interest, Desire, Action)
   - Or PAS (Problem, Agitate, Solution)
   - Or 4Ps (Picture, Promise, Proof, Push)

4. ENGAGEMENT TRIGGERS:
   - Numbers/data points
   - Contrarian angles
   - Practical takeaways
   - Emotional resonance
   - Clear CTA

5. FORMAT:
   Each post must be engaging, authentic, and shareable. NO corporate speak. Sound human.

RETURN: JSON array of objects with:
- "platform": platform name
- "text": the complete post (include hook + body + CTA)
- "hook_type": type of hook used (question/shocking/curiosity/etc)
- "framework": framework used (AIDA/PAS/etc)

Example output format:
[
    {{
        "platform": "LinkedIn",
        "text": "Did you know 87% of AI startups fail in year 1?\\n\\nHere's what the survivors do differently:\\n\\n→ Focus on one problem\\n→ Ship fast, iterate faster\\n→ Talk to users daily\\n\\nThe data is clear. Execution > Ideas.\\n\\nWhat's your #1 startup lesson? 👇",
        "hook_type": "question",
        "framework": "PAS"
    }}
]

Generate {num_variants} VIRAL posts NOW:"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a viral social media expert. You ONLY return valid JSON arrays. Your posts get 10x engagement. You use proven hooks, frameworks, and psychological triggers."
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,  # High creativity for viral content
        )

        content = response.choices[0].message.content or "[]"

        # Parse JSON response
        try:
            posts = json.loads(content)
        except json.JSONDecodeError:
            # Fallback: extract JSON from markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            posts = json.loads(content)

        # Validate and clean posts
        valid_posts = []
        for post in posts:
            if isinstance(post, dict) and "platform" in post and "text" in post:
                valid_posts.append({
                    "platform": post.get("platform", "General"),
                    "text": post.get("text", ""),
                    "hook_type": post.get("hook_type", "unknown"),
                    "framework": post.get("framework", "unknown"),
                })

        print(f"[script_gen] Generated {len(valid_posts)} viral text posts")
        return valid_posts

    except Exception as e:
        print(f"[script_gen] Error generating text posts: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


async def generate_viral_video_scripts(
    article: Dict[str, Any],
    num_variants: int = 3,
    duration: int = 20
) -> List[Dict[str, Any]]:
    """
    Generate viral video scripts with precise timing and psychological hooks.

    Args:
        article: Article data
        num_variants: Number of script variations
        duration: Target duration in seconds (15-60)

    Returns:
        List of dicts with 'script', 'hook_type', 'duration' fields
    """
    client = AsyncOpenAI()

    prompt = f"""You are a VIRAL VIDEO SCRIPT EXPERT. Your scripts get millions of views.

ARTICLE INFO:
Title: {article.get('title', '')}
Summary: {article.get('summary', '')}

TASK: Create {num_variants} VIRAL {duration}-second video scripts.

CRITICAL STRUCTURE (timing is EXACT):
Hook (0-{min(3, duration//4)}s): ULTRA-ENGAGING opening
- Question: "Did you know AI can now...?"
- Shocking: "This will change everything..."
- Curiosity: "The secret nobody tells you..."
- Pattern Interrupt: "Stop doing X. Start Y..."

Main ({min(3, duration//4)+1}-{duration*3//5}s): Core message
- Key insight/value proposition
- 1-2 main points
- Visual/concrete examples

Why ({duration*3//5+1}-{duration*4//5}s): Emotional payoff
- Why it matters to viewer
- Impact/transformation
- FOMO or aspiration

CTA ({duration*4//5+1}-{duration}s): Strong ending
- Clear next step
- Engagement driver
- Loop/hook for rewatch

PROVEN FORMULAS:
- Value Bomb: Problem → Solution → Proof → Action
- Story Arc: Setup → Conflict → Resolution → Lesson
- List Format: Hook → Point 1, 2, 3 → CTA
- Before/After: Was X → Now Y → How → Action

ENGAGEMENT TRICKS:
- First 3 seconds = hook or lose viewer
- Use "you" language
- Create curiosity gaps
- End with question/CTA for comments

RETURN: JSON array of objects:
- "script": Full script with timing labels
- "hook_type": Type of hook (question/shocking/curiosity/etc)
- "formula": Formula used (value_bomb/story/list/before_after)
- "duration": Duration in seconds
- "visual_suggestions": Brief visual ideas

Example:
[
    {{
        "script": "Hook (0-2s): Did you know 90% of AI startups fail?\\n\\nMain (3-12s): But the 10% that survive do 3 things differently. First, they ship fast. Second, they listen to users. Third, they iterate daily.\\n\\nWhy (13-17s): This isn't luck. It's a proven playbook that separates winners from losers.\\n\\nCTA (18-20s): Want to learn the full framework? Follow for daily startup lessons.",
        "hook_type": "question",
        "formula": "value_bomb",
        "duration": 20,
        "visual_suggestions": "Text overlays with stats, split screen before/after, fast cuts"
    }}
]

Generate {num_variants} VIRAL scripts NOW:"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a viral video script expert. Return ONLY valid JSON. Your scripts follow proven formulas and precise timing. Every second counts."
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.85,
        )

        content = response.choices[0].message.content or "[]"

        # Parse JSON
        try:
            scripts = json.loads(content)
        except json.JSONDecodeError:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            scripts = json.loads(content)

        # Validate scripts
        valid_scripts = []
        for script in scripts:
            if isinstance(script, dict) and "script" in script:
                valid_scripts.append({
                    "script": script.get("script", ""),
                    "hook_type": script.get("hook_type", "unknown"),
                    "formula": script.get("formula", "unknown"),
                    "duration": script.get("duration", duration),
                    "visual_suggestions": script.get("visual_suggestions", ""),
                })

        print(f"[script_gen] Generated {len(valid_scripts)} viral video scripts")
        return valid_scripts

    except Exception as e:
        print(f"[script_gen] Error generating video scripts: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


# ==================== UTILITY FUNCTIONS ====================

def get_random_hook_template(hook_type: str) -> str:
    """Get a random hook template for the specified type."""
    templates = VIRAL_HOOK_TEMPLATES.get(hook_type, [])
    return random.choice(templates) if templates else ""


def get_platform_strategy(platform: str) -> Dict[str, str]:
    """Get optimization strategy for a specific platform."""
    return PLATFORM_STRATEGIES.get(platform, PLATFORM_STRATEGIES["LinkedIn"])
