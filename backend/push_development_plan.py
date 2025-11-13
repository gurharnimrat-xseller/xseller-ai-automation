"""
Push complete development plan to Notion
Creates entries for all milestones and daily tasks
"""
from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401
import os
from datetime import datetime, timedelta
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

client = Client(auth=os.getenv("NOTION_API_KEY"))
db_id = os.getenv("NOTION_DATABASE_ID")

def create_task(title, summary, entry_type, milestone, status, owner, priority="Medium", eod_date=None):
    """Create a task entry in Notion"""
    try:
        properties = {
            "Item": {
                "title": [{"text": {"content": title}}]
            },
            "Entry Type": {
                "select": {"name": entry_type}
            },
            "Owner": {
                "rich_text": [{"text": {"content": owner}}]
            },
            "Status": {
                "status": {"name": status}
            },
            "Milestone": {
                "select": {"name": milestone}
            },
            "Priority": {
                "select": {"name": priority}
            },
            "Summary / Notes": {
                "rich_text": [{"text": {"content": summary[:2000]}}]
            }
        }

        if eod_date:
            properties["EOD Date"] = {
                "date": {"start": eod_date.isoformat()}
            }

        response = client.pages.create(
            parent={"database_id": db_id},
            properties=properties
        )

        print(f"✅ Created: {title}")
        return response

    except Exception as e:
        print(f"❌ Failed to create '{title}': {str(e)}")
        return None

# Calculate dates (starting from today)
start_date = datetime.now()

print("📋 Creating Development Plan in Notion...\n")

# ====================
# MILESTONE 0: Cloud Setup (COMPLETED)
# ====================
print("🎯 Milestone 0: Cloud Setup (COMPLETED)")

create_task(
    title="✅ M0 Complete: Cloud Infrastructure Ready",
    summary="""All cloud infrastructure is set up and working:

✅ Completed Tasks:
• GitHub repository created with 66 files migrated
• Security: Removed exposed API keys from commits
• Docker container with Python 3.11 + Node 20
• FFmpeg, OpenCV, Whisper installed
• GitHub Actions CI/CD configured
• Notion integration working
• Codespace environment ready

🎉 Result: MacBook dependency eliminated! Can work from anywhere.""",
    entry_type="Daily update",
    milestone="M0: Cloud Setup",
    status="Done",
    owner="Claude + Codex",
    priority="High",
    eod_date=start_date
)

# ====================
# MILESTONE 1: Content Scraping & Script Generation
# ====================
print("\n🎯 Milestone 1: Content Scraping & Script Generation")
m1_start = start_date + timedelta(days=1)

# Day 1: News Scraper
create_task(
    title="Day 1: Build News Scraper",
    summary="""Build news scraper to fetch latest crypto/market news:

Tasks:
• Set up NewsAPI integration (free tier)
• Create scraper for cryptocurrency news
• Create scraper for stock market news
• Filter by relevance and recency
• Store articles in SQLite database
• Add caching to avoid duplicate fetches

Acceptance Criteria:
• Can fetch top 10 news articles on demand
• Articles stored with title, description, URL, published date
• Duplicate detection working
• Test with Bitcoin and Tesla news""",
    entry_type="Task",
    milestone="M1: Content",
    status="Todo",
    owner="Codex",
    priority="High",
    eod_date=m1_start
)

# Day 2: Content Analysis
create_task(
    title="Day 2: Content Analysis & Filtering",
    summary="""Analyze and filter scraped content for video creation:

Tasks:
• Build sentiment analysis (positive/negative/neutral)
• Score articles by engagement potential (1-10)
• Filter out low-quality or duplicate content
• Extract key facts and figures from articles
• Identify trending topics across multiple sources

Acceptance Criteria:
• Can analyze 100 articles in < 5 seconds
• Sentiment accuracy > 80%
• Top 3 articles selected automatically
• Key facts extracted and formatted""",
    entry_type="Task",
    milestone="M1: Content",
    status="Todo",
    owner="Codex",
    priority="High",
    eod_date=m1_start + timedelta(days=1)
)

# Day 3: Script Generator
create_task(
    title="Day 3: AI Script Generation",
    summary="""Build AI script generator using GPT-4:

Tasks:
• Create prompt templates for different content types
• Build script generator with GPT-4 integration
• Generate 30-60 second video scripts
• Add hooks (attention-grabbing openings)
• Add CTAs (calls-to-action)
• Format for TTS (pauses, emphasis)

Script Structure:
1. Hook (3-5 sec): "Breaking news in crypto!"
2. Context (10 sec): Background info
3. Main Point (30 sec): Key information
4. CTA (5 sec): "Follow for more updates!"

Acceptance Criteria:
• Generate script from article in < 3 seconds
• Script length 150-200 words (60 sec @ 180 WPM)
• Hook engagement tested with 5 samples
• TTS-friendly formatting (proper punctuation)""",
    entry_type="Task",
    milestone="M1: Content",
    status="Todo",
    owner="Claude",
    priority="High",
    eod_date=m1_start + timedelta(days=2)
)

# Day 4: Testing & Refinement
create_task(
    title="Day 4: Test Complete Content Pipeline",
    summary="""End-to-end testing of content generation:

Tests:
• Scrape 20 articles from 3 sources
• Analyze and rank all articles
• Generate scripts for top 3 articles
• Human review of script quality
• Adjust prompts based on feedback
• Test edge cases (breaking news, updates)

Success Metrics:
• Pipeline completes in < 30 seconds
• 80% of scripts are "video-ready" without edits
• No crashes or errors in 10 consecutive runs
• Scripts are engaging and accurate""",
    entry_type="Task",
    milestone="M1: Content",
    status="Todo",
    owner="Claude + Codex",
    priority="High",
    eod_date=m1_start + timedelta(days=3)
)

# ====================
# MILESTONE 2: Media Assets (Stock & AI)
# ====================
print("\n🎯 Milestone 2: Media Assets")
m2_start = m1_start + timedelta(days=4)

# Day 5: Stock Media Integration
create_task(
    title="Day 5: Stock Media APIs",
    summary="""Integrate Pexels and other stock media APIs:

Tasks:
• Set up Pexels API integration
• Set up Pixabay API (backup)
• Build keyword extraction from scripts
• Search for relevant videos/images
• Download and cache media files
• Handle API rate limits

Features:
• Auto-select videos based on script keywords
• Fallback to images if no videos found
• Cache popular media to save API calls
• 4K video support for quality

Acceptance Criteria:
• Can fetch 10 relevant videos in < 5 seconds
• 90% relevance match to keywords
• Handles rate limits gracefully
• No duplicate media in same video""",
    entry_type="Task",
    milestone="M2: Media",
    status="Todo",
    owner="Codex",
    priority="High",
    eod_date=m2_start
)

# Day 6: Image Generation
create_task(
    title="Day 6: AI Image Generation (Optional)",
    summary="""Add AI image generation for custom visuals:

Tasks:
• DALL-E 3 API integration
• Stable Diffusion local setup (optional)
• Generate custom thumbnails
• Generate overlay graphics
• Style consistency across images

Use Cases:
• Custom thumbnails for each video
• Charts/graphs for financial data
• Text overlays with key statistics
• Brand watermarks

Acceptance Criteria:
• Generate 1 image in < 10 seconds
• Images are 1920x1080 (HD)
• Style is consistent across videos
• Text is readable in generated images""",
    entry_type="Task",
    milestone="M2: Media",
    status="Todo",
    owner="Claude",
    priority="Medium",
    eod_date=m2_start + timedelta(days=1)
)

# Day 7: Media Processing
create_task(
    title="Day 7: Media Processing & Optimization",
    summary="""Process and optimize all media assets:

Tasks:
• Resize videos to 1080x1920 (vertical format)
• Compress without quality loss
• Add transitions between clips
• Color correction and grading
• Audio normalization
• Generate preview thumbnails

Technical:
• FFmpeg for video processing
• OpenCV for image processing
• Target file size: < 50MB per video
• Format: MP4 (H.264)

Acceptance Criteria:
• Process 10 videos in < 30 seconds
• Output quality: High (1080p minimum)
• File size optimized for mobile
• Smooth transitions (1 sec fade)""",
    entry_type="Task",
    milestone="M2: Media",
    status="Todo",
    owner="Codex",
    priority="High",
    eod_date=m2_start + timedelta(days=2)
)

# ====================
# MILESTONE 3: Video Production
# ====================
print("\n🎯 Milestone 3: Video Production")
m3_start = m2_start + timedelta(days=3)

# Day 8: Text-to-Speech
create_task(
    title="Day 8: Professional TTS Integration",
    summary="""Integrate high-quality text-to-speech:

Tasks:
• ElevenLabs API integration (primary)
• OpenAI TTS integration (backup)
• Voice selection system
• Audio timing and pacing
• Emphasis and emotion control

Voice Options:
• ElevenLabs: Charlotte (British female), Charlie (British male)
• OpenAI: Fable (British male), Nova (female)
• Auto-select based on content type

Features:
• Adjust speech rate (0.8x - 1.2x)
• Add pauses for emphasis
• Emotion tuning (excited, calm, serious)
• Audio quality: 44.1kHz, 128kbps

Acceptance Criteria:
• Generate 60-sec audio in < 5 seconds
• Voice sounds natural and engaging
• Proper emphasis on key words
• No robotic artifacts""",
    entry_type="Task",
    milestone="M3: Video",
    status="Todo",
    owner="Claude",
    priority="High",
    eod_date=m3_start
)

# Day 9: Video Assembly
create_task(
    title="Day 9: Video Assembly Pipeline",
    summary="""Build complete video assembly system:

Tasks:
• Sync media with TTS audio
• Add captions/subtitles (auto-generated)
• Add background music (royalty-free)
• Add intro/outro templates
• Export final video

Video Structure:
1. Intro (2 sec): Brand logo + sound effect
2. Main Content (50 sec): Media + voiceover + captions
3. Outro (3 sec): CTA + social handles

Technical:
• MoviePy for video editing
• FFmpeg for rendering
• Whisper for caption timing
• Output: 1080x1920 MP4

Acceptance Criteria:
• Assemble video in < 60 seconds
• Perfect audio-visual sync
• Captions are accurate (95%+)
• Smooth playback, no glitches""",
    entry_type="Task",
    milestone="M3: Video",
    status="Todo",
    owner="Codex",
    priority="High",
    eod_date=m3_start + timedelta(days=1)
)

# Day 10: Competitor Analysis Replication
create_task(
    title="Day 10: Match Competitor Quality",
    summary="""Replicate competitor video style and quality:

Analyze:
• @mrwhosetheboss style (tech news)
• @ColdFusion style (financial news)
• Pacing, transitions, music
• Caption style and positioning
• Thumbnail design

Replicate:
• Similar video pacing (fast cuts)
• Professional transitions
• Engaging caption style
• High-energy background music
• Compelling thumbnails

A/B Testing:
• Create 2 versions of same video
• Test different music tracks
• Test different caption styles
• Measure engagement

Acceptance Criteria:
• Side-by-side comparison shows similar quality
• Video feels professional, not automated
• 80% of test viewers can't tell it's AI-generated""",
    entry_type="Task",
    milestone="M3: Video",
    status="Todo",
    owner="Claude + Codex",
    priority="High",
    eod_date=m3_start + timedelta(days=2)
)

# Day 11: Batch Generation
create_task(
    title="Day 11: Batch Video Generation",
    summary="""Build system to generate multiple videos:

Tasks:
• Queue system for batch processing
• Parallel video generation (3-5 at once)
• Progress tracking and logging
• Error handling and retry logic
• Storage and organization

Features:
• Generate 10 videos overnight
• Auto-retry failed videos
• Organize by date and topic
• Generate analytics report
• Email notification on completion

Acceptance Criteria:
• Generate 10 videos in < 20 minutes
• 95% success rate
• Failed videos auto-retry once
• All videos stored with metadata""",
    entry_type="Task",
    milestone="M3: Video",
    status="Todo",
    owner="Codex",
    priority="High",
    eod_date=m3_start + timedelta(days=3)
)

# ====================
# MILESTONE 4: Quality & Review
# ====================
print("\n🎯 Milestone 4: Quality Control & Review")
m4_start = m3_start + timedelta(days=4)

# Day 12: Quality Checks
create_task(
    title="Day 12: Automated Quality Checks",
    summary="""Build automated quality control system:

Checks:
• Video plays correctly (no corruption)
• Audio levels are normalized (-16 LUFS)
• Captions are synced (< 0.5 sec offset)
• No dead air (silence > 3 seconds)
• Duration is within range (45-65 sec)
• File size is reasonable (< 50MB)

Technical Checks:
• Video codec: H.264
• Resolution: 1080x1920
• Frame rate: 30 FPS
• Audio codec: AAC
• Bitrate: 4-6 Mbps

Acceptance Criteria:
• Check 1 video in < 2 seconds
• Flag issues automatically
• Generate QC report
• Reject < 5% of videos""",
    entry_type="Task",
    milestone="M4: Review",
    status="Todo",
    owner="Codex",
    priority="High",
    eod_date=m4_start
)

# Day 13: Review Dashboard
create_task(
    title="Day 13: Web Review Dashboard",
    summary="""Build web interface for video review:

Features:
• View all generated videos
• Play video in browser
• See video metadata (title, script, sources)
• Approve/reject/edit buttons
• Batch approval
• Schedule for publishing

UI Components:
• Video player with controls
• Script viewer (side-by-side)
• Edit script and regenerate
• Thumbnail preview
• Publishing queue

Tech Stack:
• Next.js frontend (already set up)
• FastAPI backend (already set up)
• Video.js for playback
• Drag-and-drop for queue ordering

Acceptance Criteria:
• Can review 10 videos in < 5 minutes
• Smooth video playback
• Edit and regenerate working
• Mobile-friendly interface""",
    entry_type="Task",
    milestone="M4: Review",
    status="Todo",
    owner="Claude",
    priority="High",
    eod_date=m4_start + timedelta(days=1)
)

# Day 14: Feedback Loop
create_task(
    title="Day 14: Feedback & Improvement System",
    summary="""Build system to learn from feedback:

Features:
• Track which videos perform best
• Analyze successful patterns
• A/B test script variations
• Track engagement metrics
• Auto-improve prompts

Analytics:
• Views, likes, shares, comments
• Audience retention graph
• Click-through rate on CTAs
• Best performing topics
• Optimal posting times

Machine Learning:
• Store all metadata in database
• Track correlation between features and performance
• Adjust script prompts based on data
• Optimize video length based on retention

Acceptance Criteria:
• Track performance for 20+ videos
• Identify top 3 success factors
• Auto-adjust 1 parameter based on data
• Performance improves by 10% over baseline""",
    entry_type="Task",
    milestone="M4: Review",
    status="Todo",
    owner="Claude + Codex",
    priority="Medium",
    eod_date=m4_start + timedelta(days=2)
)

# ====================
# MILESTONE 5: Publishing & Automation
# ====================
print("\n🎯 Milestone 5: Publishing & Automation")
m5_start = m4_start + timedelta(days=3)

# Day 15: Social Media APIs
create_task(
    title="Day 15: Social Media API Integration",
    summary="""Integrate with social media platforms:

Platforms:
• X (Twitter) - video + text posts
• Instagram Reels - via Meta Graph API
• TikTok - TikTok API for Business
• YouTube Shorts - YouTube Data API

Tasks:
• OAuth authentication for each platform
• Video upload endpoints
• Caption and hashtag optimization
• Thumbnail upload
• Post scheduling

Features:
• Cross-post to multiple platforms
• Platform-specific optimizations
• Hashtag generation
• Best time to post calculation
• Rate limit handling

Acceptance Criteria:
• Post to 1 platform successfully
• Video appears correctly in feed
• Captions and hashtags applied
• Thumbnail displays properly""",
    entry_type="Task",
    milestone="M5: Publishing",
    status="Todo",
    owner="Codex",
    priority="High",
    eod_date=m5_start
)

# Day 16: Scheduling System
create_task(
    title="Day 16: Automated Scheduling",
    summary="""Build intelligent scheduling system:

Features:
• Schedule posts for optimal times
• Queue management (FIFO, priority)
• Platform-specific timing
• Timezone awareness (global audience)
• Backup queue (if primary fails)

Smart Scheduling:
• Analyze audience activity patterns
• Post when engagement is highest
• Stagger posts across platforms
• Avoid posting too frequently
• Weekend vs weekday optimization

Calendar:
• Visual calendar view
• Drag-and-drop scheduling
• Bulk schedule (10 videos at once)
• Recurring schedules
• Holiday awareness (skip or boost)

Acceptance Criteria:
• Schedule 7 days of posts in < 2 minutes
• Posts go live at correct times
• Handles timezone conversions
• Reschedule if platform is down""",
    entry_type="Task",
    milestone="M5: Publishing",
    status="Todo",
    owner="Claude",
    priority="High",
    eod_date=m5_start + timedelta(days=1)
)

# Day 17: Monitoring & Alerts
create_task(
    title="Day 17: Monitoring & Notification System",
    summary="""Build monitoring and alert system:

Monitoring:
• Video generation status
• Publishing success/failure
• API usage and quotas
• System health (CPU, memory, disk)
• Error logs and debugging

Notifications:
• Email alerts for failures
• Slack/Discord notifications
• Daily summary reports
• Weekly performance digest
• Notion daily updates (already working!)

Dashboard:
• Real-time status display
• Recent activity log
• Error tracking
• Cost monitoring (API usage)
• Performance metrics

Acceptance Criteria:
• Email alert sent within 1 minute of failure
• Daily summary sent at 9 AM
• Dashboard loads in < 2 seconds
• All metrics are accurate""",
    entry_type="Task",
    milestone="M5: Publishing",
    status="Todo",
    owner="Codex",
    priority="Medium",
    eod_date=m5_start + timedelta(days=2)
)

# Day 18: Full Automation
create_task(
    title="Day 18: Complete End-to-End Automation",
    summary="""Put it all together - fully automated pipeline:

Workflow:
1. Scrape news (every 6 hours)
2. Generate scripts (top 3 articles)
3. Fetch media assets
4. Generate videos
5. Quality check
6. Add to review queue
7. Auto-approve (if score > 8/10)
8. Schedule for publishing
9. Post at optimal time
10. Track performance
11. Send daily report

Automation:
• GitHub Actions cron job (or similar)
• Runs 4x daily (6 AM, 12 PM, 6 PM, 12 AM)
• Zero manual intervention needed
• Self-healing (auto-retry failures)

Failsafe:
• Human review for low-score videos
• Manual override always available
• Pause button for emergencies
• Rollback to previous version

Acceptance Criteria:
• Run for 7 days with 0 manual intervention
• Generate 28 videos (4/day)
• 90% auto-approval rate
• 0 critical failures
• Daily Notion updates working""",
    entry_type="Task",
    milestone="M5: Publishing",
    status="Todo",
    owner="Claude + Codex",
    priority="High",
    eod_date=m5_start + timedelta(days=3)
)

# ====================
# FINAL MILESTONE
# ====================
create_task(
    title="Day 19-21: Testing, Polish & Launch",
    summary="""Final testing and launch preparation:

Testing (2 days):
• Load testing (100 videos)
• Stress testing (failures, rate limits)
• Security audit (API keys, auth)
• User acceptance testing
• Bug fixes

Polish (1 day):
• Documentation (README, API docs)
• Video tutorials
• Deployment guide
• Cost optimization
• Performance tuning

Launch:
• Deploy to production
• Enable automation
• Monitor first 48 hours closely
• Gather feedback
• Quick iterations

Success Criteria:
• All tests pass
• Documentation complete
• First 100 videos generated successfully
• < 5% error rate
• Positive user feedback

🎉 PROJECT COMPLETE!""",
    entry_type="Task",
    milestone="M5: Publishing",
    status="Todo",
    owner="Claude + Codex",
    priority="High",
    eod_date=m5_start + timedelta(days=6)
)

# ====================
# PLANNING DOCUMENTS
# ====================
print("\n📋 Creating Planning Documents")

create_task(
    title="🗺️ Project Roadmap Overview",
    summary="""Complete Xseller.ai Development Roadmap

Timeline: 21 days (3 weeks)
Team: Claude (AI Dev) + Codex (GitHub Copilot) + Gurvinder (Product Owner)

Milestones:
✅ M0: Cloud Setup (Day 0) - COMPLETE
📋 M1: Content (Days 1-4) - News scraping, script generation
🎨 M2: Media (Days 5-7) - Stock videos, AI images, processing
🎬 M3: Video (Days 8-11) - TTS, assembly, batch generation
✅ M4: Review (Days 12-14) - Quality checks, dashboard, feedback
🚀 M5: Publishing (Days 15-18) - APIs, scheduling, automation
🎉 Final: Testing & Launch (Days 19-21)

Budget:
• OpenAI API: ~$50/month
• ElevenLabs: ~$22/month (Starter plan)
• Pexels: Free
• GitHub: Free (Codespaces 60 hrs/month)
• Total: ~$75/month

Success Metrics:
• Generate 4 videos/day automatically
• 90% quality approval rate
• < 5% error rate
• Fully autonomous operation
• Cost < $100/month

Next Steps:
1. Start M1 tomorrow
2. Daily Notion updates
3. Weekly demos
4. Ship fast, iterate faster!""",
    entry_type="Plan structure",
    milestone="M0: Cloud Setup",
    status="Done",
    owner="Claude",
    priority="High",
    eod_date=start_date
)

create_task(
    title="🎯 Weekly Sprint Planning - Week 1",
    summary="""Week 1 Goals: Content + Media Pipeline

Focus Areas:
• M1: Content scraping and script generation (Days 1-4)
• M2: Media asset collection and processing (Days 5-7)

Key Deliverables:
• Working news scraper
• AI script generator
• Stock media integration
• Media processing pipeline

Daily Standups:
• What did you ship yesterday?
• What are you shipping today?
• Any blockers?

Success = End of week demo:
• Fetch news article
• Generate script
• Fetch relevant media
• Show proof-of-concept

Team:
• Codex: Backend systems, APIs, data
• Claude: AI prompts, integration, testing
• Gurvinder: Review, feedback, priorities""",
    entry_type="Plan structure",
    milestone="M1: Content",
    status="Todo",
    owner="Claude + Codex",
    priority="High",
    eod_date=m1_start
)

create_task(
    title="🎯 Weekly Sprint Planning - Week 2",
    summary="""Week 2 Goals: Video Production + Quality

Focus Areas:
• M3: Video production pipeline (Days 8-11)
• M4: Quality control and review (Days 12-14)

Key Deliverables:
• Professional TTS integration
• Complete video assembly
• Batch generation system
• Quality control automation
• Web review dashboard

Mid-sprint Demo (Day 10):
• Show first complete video
• Compare with competitor
• Get feedback, iterate

Success = End of week demo:
• Generate 10 videos in batch
• All pass quality checks
• Review in web dashboard
• Ready for publishing

Team:
• Codex: Video processing, QC, infrastructure
• Claude: TTS, UI, user experience
• Gurvinder: Quality review, final approval""",
    entry_type="Plan structure",
    milestone="M3: Video",
    status="Todo",
    owner="Claude + Codex",
    priority="High",
    eod_date=m3_start
)

create_task(
    title="🎯 Weekly Sprint Planning - Week 3",
    summary="""Week 3 Goals: Publishing + Automation + Launch

Focus Areas:
• M5: Publishing and automation (Days 15-18)
• Final: Testing, polish, launch (Days 19-21)

Key Deliverables:
• Social media integrations
• Automated scheduling
• Monitoring and alerts
• Complete end-to-end automation
• Documentation and launch

Daily Goals:
• Day 15: Twitter integration working
• Day 16: Scheduler operational
• Day 17: Monitoring dashboard live
• Day 18: Full automation test
• Day 19-20: Testing and bug fixes
• Day 21: LAUNCH! 🚀

Success = Launch Day:
• System runs 24/7 autonomously
• Generates 4 videos per day
• Posts to all platforms
• Zero manual intervention needed
• Notion updates automatically
• You can focus on strategy!

Team:
• Codex: APIs, automation, deployment
• Claude: Testing, docs, final polish
• Gurvinder: Launch strategy, marketing""",
    entry_type="Plan structure",
    milestone="M5: Publishing",
    status="Todo",
    owner="Claude + Codex",
    priority="High",
    eod_date=m5_start
)

print("\n✅ Development plan pushed to Notion!")
print(f"📊 View your plan: https://notion.so/{db_id.replace('-', '')}")
print("\n🎯 Next Steps:")
print("  1. Review plan in Notion")
print("  2. Adjust dates/priorities as needed")
print("  3. Start M1 Day 1 tomorrow!")
print("  4. Daily updates will post automatically")
