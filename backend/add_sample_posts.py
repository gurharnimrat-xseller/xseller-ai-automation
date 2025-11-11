"""Add sample posts to the database for testing."""

from app.database import engine
from app.models import Post
from sqlmodel import Session
from datetime import datetime

# Create sample posts
sample_posts = [
    Post(
        kind="text",
        title="OpenAI Releases GPT-4 Turbo",
        body="OpenAI just announced GPT-4 Turbo with improved performance and lower costs. This update brings enhanced reasoning capabilities and faster response times. #AI #OpenAI",
        source_url="https://openai.com/blog",
        platforms=["X", "LinkedIn"],
        tags=["AI", "Technology"],
        status="draft",
    ),
    Post(
        kind="text",
        title="Google AI Introduces Gemini Pro",
        body="Google's latest AI model Gemini Pro offers multimodal capabilities. The model can understand text, images, and video simultaneously. #MachineLearning #Google",
        source_url="https://deepmind.google",
        platforms=["Instagram", "Facebook"],
        tags=["AI", "Google"],
        status="draft",
    ),
    Post(
        kind="video",
        title="The Future of AI in Healthcare",
        body="AI is revolutionizing healthcare with diagnostic tools, drug discovery, and personalized treatment plans. Video script: [Hook] Healthcare is changing. [Main] AI helps doctors diagnose faster. [Why] Better outcomes for patients. [CTA] Learn more today!",
        source_url="https://techcrunch.com/ai",
        platforms=["YouTube", "TikTok"],
        tags=["AI", "Healthcare"],
        status="approved",
    ),
    Post(
        kind="text",
        title="MIT Develops Self-Driving Car AI",
        body="MIT researchers have created an AI system that can navigate complex urban environments. The system uses advanced sensor fusion and deep learning to make real-time decisions. #MIT #AutonomousVehicles",
        source_url="https://www.technologyreview.com",
        platforms=["LinkedIn", "X"],
        tags=["AI", "Transportation"],
        status="draft",
    ),
]

with Session(engine) as session:
    for post in sample_posts:
        session.add(post)
    session.commit()
    print(f"✅ Created {len(sample_posts)} sample posts")

from agents.checks.router import should_offload, offload_to_gemini  # guardrails
