"""
Complete M4 & M5 with detailed tasks + add missing metadata
"""
import os
from datetime import datetime, timedelta
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

client = Client(auth=os.getenv("NOTION_API_KEY"))
db_id = os.getenv("NOTION_DATABASE_ID")

def create_detailed_task(title, summary, milestone, status, owner, priority, eod_date, effort_hours=None, tags=None, acceptance_criteria=None):
    """Create a detailed task with all metadata"""
    try:
        properties = {
            "Item": {
                "title": [{"text": {"content": title}}]
            },
            "Entry Type": {
                "select": {"name": "Task"}
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
                "rich_text": [{"text": {"content": summary[:1900]}}]  # Leave buffer for safety
            },
            "EOD Date": {
                "date": {"start": eod_date.isoformat()}
            }
        }

        # Add effort hours if provided
        if effort_hours:
            properties["Effort (hours)"] = {"number": effort_hours}

        # Add tags if provided
        if tags:
            properties["Tags"] = {
                "multi_select": [{"name": tag} for tag in tags]
            }

        # Add acceptance criteria to summary
        if acceptance_criteria:
            properties["Acceptance Criteria"] = {
                "rich_text": [{"text": {"content": acceptance_criteria[:2000]}}]
            }

        response = client.pages.create(
            parent={"database_id": db_id},
            properties=properties
        )

        print(f"✅ {title}")
        return response

    except Exception as e:
        print(f"❌ Failed: {title} - {str(e)}")
        return None

# Calculate dates
today = datetime.now()
m4_start = today + timedelta(days=22)  # Week 4
m5_start = today + timedelta(days=29)  # Week 5

print("="*80)
print("🚀 COMPLETING M4 & M5 WITH FULL DETAILS")
print("="*80)

# ==========================================
# MILESTONE 4: REVIEW INTERFACE (Week 4)
# ==========================================
print("\n📋 MILESTONE 4: Review Interface (Week 4)")

create_detailed_task(
    title="M4A: Queue Enhancement UI - Video Preview System",
    summary="""Build comprehensive video review interface in Next.js frontend

🎯 Goal: Create intuitive UI for reviewing generated videos before approval

📋 Tasks:
1. Video Preview Player
   • Integrate Video.js or React Player
   • Support 1080x1920 vertical format
   • Controls: play, pause, seek, volume
   • Fullscreen mode for mobile testing
   • Playback speed control (0.5x - 2x)

2. Script Display Panel
   • Show script text alongside video
   • Highlight current segment during playback
   • Inline editing capability (contentEditable)
   • Word count and timing display
   • Save changes with version history

3. B-Roll Thumbnail Grid
   • Display all B-roll clips used
   • Show timestamp ranges for each clip
   • Click to preview individual clip
   • Swap clip button (search alternative)
   • Add/remove clips functionality

4. Voice Sample Playback
   • Separate audio player for voice only
   • Compare with original script text
   • Show audio waveform visualization
   • Identify pauses and emphasis points
   • Re-generate voice button

5. Approve/Reject Workflow
   • Large approve button (green)
   • Reject with reason (opens feedback modal)
   • Request changes (specific issues)
   • Save draft for later review
   • Keyboard shortcuts (A=approve, R=reject)

🔧 Technical Implementation:
• Frontend: Next.js + TypeScript + Tailwind CSS
• Video Player: Video.js (customized for vertical)
• State Management: React Context or Zustand
• API: FastAPI endpoints for CRUD operations
• Real-time updates: WebSocket for queue changes

📁 File Structure:
frontend/components/VideoPreview.tsx
frontend/components/ScriptEditor.tsx
frontend/components/BRollGrid.tsx
frontend/components/ApprovalButtons.tsx
frontend/hooks/useVideoQueue.ts
frontend/api/videoQueue.ts

✅ Acceptance Criteria:
• Video plays smoothly in browser (no lag)
• Script editing saves immediately (debounced)
• B-roll grid shows all clips with thumbnails
• Approve/reject updates database instantly
• Keyboard shortcuts work
• Mobile responsive (works on phone)
• Can review 10 videos in < 5 minutes
• Zero bugs in user testing

📊 Estimated Effort: 16 hours (2 days)

🧪 Testing:
• Load test with 50 videos in queue
• Test on Chrome, Safari, Firefox
• Test on iPhone and Android
• Verify video playback quality
• Test keyboard shortcuts
• Check accessibility (WCAG AA)""",
    milestone="M4: Review",
    status="Todo",
    owner="Claude",
    priority="High",
    eod_date=m4_start + timedelta(days=1),
    effort_hours=16,
    tags=["frontend", "ui", "react", "video"],
    acceptance_criteria="Video plays smoothly, script edits save, B-roll grid works, approve/reject instant, keyboard shortcuts, mobile responsive"
)

create_detailed_task(
    title="M4B: Structured Feedback Modal - Issue Taxonomy System",
    summary="""Build feedback collection system for targeted improvements

🎯 Goal: Capture specific, actionable feedback for regeneration

📋 Tasks:
1. Feedback Modal Design
   • Opens when "Request Changes" clicked
   • Categorized feedback sections
   • Visual issue markers on video timeline
   • Before/after comparison preview
   • Submit with confidence (regenerate now vs later)

2. Feedback Taxonomy
   Categories:

   A) Script Issues:
      □ Hook not engaging enough
      □ Context too long/short
      □ Main point unclear
      □ CTA not compelling
      □ Tone mismatch (too formal/casual)
      □ Factual errors
      □ Grammar/spelling issues

   B) Voice Issues:
      □ Speed too fast/slow
      □ Energy too high/low
      □ Pronunciation errors
      □ Awkward pauses
      □ Wrong emphasis
      □ Voice mismatch (want different voice)

   C) B-Roll Issues:
      □ Clip not relevant to content
      □ Low quality/blurry
      □ Wrong orientation (not vertical)
      □ Scene change too fast/slow
      □ Needs different keyword search
      □ Missing B-roll for segment

   D) Audio Mix Issues:
      □ Voice too quiet/loud
      □ Music too prominent
      □ Background noise
      □ Audio sync off
      □ Transitions jarring

   E) Text Overlay Issues:
      □ Text not readable
      □ Wrong timing
      □ Emphasis on wrong words
      □ Style doesn't match
      □ Too many/few overlays

3. Rating System
   • Overall quality: 1-5 stars
   • Individual components: 1-5 stars each
     - Script: ⭐⭐⭐⭐⭐
     - Voice: ⭐⭐⭐⭐⭐
     - B-roll: ⭐⭐⭐⭐⭐
     - Audio Mix: ⭐⭐⭐⭐⭐
     - Text Overlays: ⭐⭐⭐⭐⭐
   • Auto-calculate weighted average

4. Free-Form Notes
   • Text area for additional comments
   • Attach screenshots (drag-drop)
   • Tag team members (@mention)
   • Link to reference videos
   • Save as template for recurring issues

5. Submission Actions
   • Regenerate Now (high priority queue)
   • Save Feedback (review later)
   • Minor Edits Only (don't regenerate)
   • Approve with Notes (track for learning)

🔧 Technical Implementation:
• Modal: Headless UI + Tailwind
• Form: React Hook Form + Zod validation
• Storage: PostgreSQL feedback table
• Analytics: Track most common issues
• ML: Cluster feedback for pattern detection

📁 File Structure:
frontend/components/FeedbackModal.tsx
frontend/components/FeedbackTaxonomy.tsx
frontend/components/RatingStars.tsx
frontend/types/feedback.ts
backend/app/models/feedback.py
backend/app/routes/feedback.py

✅ Acceptance Criteria:
• All feedback categories present
• Can select multiple issues per category
• Rating system intuitive (star clicks)
• Free-form notes support markdown
• Submission stores in database
• Feedback visible in video history
• Can filter videos by feedback type
• Analytics show top 5 issues

📊 Estimated Effort: 8 hours (1 day)

🧪 Testing:
• Submit feedback for 10 test videos
• Verify all categories work
• Check database storage
• Test rating calculations
• Validate required fields
• Test with missing data""",
    milestone="M4: Review",
    status="Todo",
    owner="Claude",
    priority="High",
    eod_date=m4_start + timedelta(days=2),
    effort_hours=8,
    tags=["frontend", "forms", "feedback", "ui"],
    acceptance_criteria="All categories work, ratings intuitive, notes save, database stores feedback, can filter by issue type"
)

create_detailed_task(
    title="M4C: Regeneration Backend - Feedback-Driven Improvements",
    summary="""Build intelligent regeneration system that applies feedback

🎯 Goal: Automatically improve videos based on structured feedback

📋 Tasks:
1. Feedback Parser
   • Parse structured feedback JSON
   • Extract actionable changes
   • Prioritize changes by impact
   • Group related issues
   • Generate regeneration plan

2. Script Adjustment Engine
   If feedback includes script issues:

   A) Hook Issues:
      • Regenerate hook with "more engaging" prompt
      • Try 3 variations, score by engagement
      • A/B test against original

   B) Tone Issues:
      • Adjust prompt: "more casual" or "more professional"
      • Maintain key facts
      • Re-check word count

   C) Length Issues:
      • "Expand context" or "trim to essentials"
      • Preserve hook and CTA
      • Verify 30-60 sec target

   D) Factual Errors:
      • Flag for human review
      • Don't auto-regenerate (safety)
      • Provide correction interface

3. Voice Re-generation
   If feedback includes voice issues:

   A) Speed Adjustment:
      • Too fast: reduce speed to 0.9x
      • Too slow: increase to 1.1x
      • Re-export audio

   B) Energy Adjustment:
      • Too high: reduce stability to 0.6
      • Too low: increase stability to 0.4
      • Test with sample

   C) Voice Change:
      • Switch to alternative voice
      • Re-generate entire audio
      • Keep timing sync

   D) Pronunciation Fixes:
      • Use SSML tags for pronunciation
      • Add phonetic spelling
      • Test problematic words

4. B-Roll Replacement
   If feedback includes B-roll issues:

   A) Relevance Issues:
      • Use feedback notes as new search term
      • Re-search Artlist with improved keywords
      • Preview top 3 alternatives
      • Auto-select highest quality

   B) Quality Issues:
      • Filter for 4K minimum
      • Check resolution before download
      • Reject < 1080p vertical

   C) Timing Issues:
      • Adjust sync engine parameters
      • Longer/shorter clip duration
      • Adjust fade transition timing

5. Reassembly Pipeline
   • Keep unchanged components
   • Replace only flagged segments
   • Re-run FFmpeg assembly
   • Re-run quality checks
   • Compare before/after
   • Log all changes for learning

6. Version Control
   • Store original video (v1)
   • Store regenerated video (v2, v3, ...)
   • Track what changed between versions
   • Allow rollback to previous version
   • Compare metrics (v2 vs v1 performance)

7. Learning Loop
   • Track: Feedback → Changes → Approval
   • Identify patterns:
     - "Hook issue" + "regenerate" → approved 80%
     - "B-roll issue" → approved 95%
   • Update default prompts based on patterns
   • Build knowledge base of fixes
   • Auto-suggest fixes for common issues

🔧 Technical Implementation:
• Backend: Python + FastAPI
• Queue: Celery for async regeneration
• Storage: S3 for video versions
• Diff: Video comparison library
• ML: Scikit-learn for pattern detection

📁 File Structure:
backend/app/feedback_parser.py
backend/app/script_adjuster.py
backend/app/voice_regenerator.py
backend/app/broll_replacer.py
backend/app/reassembly.py
backend/app/version_control.py
backend/app/learning_loop.py

✅ Acceptance Criteria:
• Feedback JSON parsed correctly
• Script adjustments applied accurately
• Voice regeneration respects parameters
• B-roll replaced with better clips
• Reassembly produces valid video
• Version history tracked
• Can compare v1 vs v2 side-by-side
• Learning loop improves over time (test with 50 videos)
• 80%+ of regenerations approved

📊 Estimated Effort: 16 hours (2 days)

🧪 Testing:
• Test each feedback category separately
• Submit 10 videos with different issues
• Verify each issue type regenerates correctly
• Check version history accuracy
• Test rollback functionality
• Measure improvement rate over 50 videos""",
    milestone="M4: Review",
    status="Todo",
    owner="Codex",
    priority="High",
    eod_date=m4_start + timedelta(days=4),
    effort_hours=16,
    tags=["backend", "ml", "feedback", "regeneration"],
    acceptance_criteria="Feedback parsed, script adjusts, voice regenerates, B-roll replaces, reassembly works, versions tracked, 80% approval"
)

# ==========================================
# MILESTONE 5: PUBLISHING & AUTOMATION (Week 5)
# ==========================================
print("\n📋 MILESTONE 5: Publishing & Automation (Week 5)")

create_detailed_task(
    title="M5A: Multi-Platform Publishing - Publer Integration",
    summary="""Integrate Publer API for automated social media posting

🎯 Goal: Post approved videos to all platforms automatically

📋 Tasks:
1. Publer API Setup
   • Create Publer account (free tier)
   • Connect social accounts:
     - YouTube (Shorts)
     - TikTok
     - Instagram (Reels)
     - Facebook (Reels)
     - LinkedIn (Video)
   • Generate API key
   • Test authentication

2. Platform-Specific Formatting

   A) YouTube Shorts:
      • Format: 9:16, max 60s
      • Title: SEO optimized (50 chars)
      • Description: Full with hashtags
      • Hashtags: #Shorts #AI #Tech (max 15)
      • Thumbnail: Custom 1080x1920
      • Category: Science & Technology
      • Visibility: Public

   B) TikTok:
      • Format: 9:16, max 60s
      • Caption: Engaging (150 chars)
      • Hashtags: Trending (5-8)
      • Cover: Auto-select best frame
      • Privacy: Public
      • Comments: Enabled
      • Duet/Stitch: Enabled

   C) Instagram Reels:
      • Format: 9:16, max 90s
      • Caption: Branded (2200 chars max)
      • Hashtags: Mix of popular + niche (30 max)
      • Cover: Custom frame
      • Location: Add if relevant
      • Tag: Brands mentioned

   D) Facebook Reels:
      • Format: 9:16, max 60s
      • Caption: Same as Instagram
      • Hashtags: 5-10
      • Thumbnail: Auto
      • Audience: Public

   E) LinkedIn:
      • Format: 16:9 (re-export!)
      • Duration: Up to 10 min (use 60s)
      • Caption: Professional tone
      • Hashtags: Industry specific
      • Visibility: Public

3. Video Conversion Service
   • Most platforms: Use existing 1080x1920
   • LinkedIn: Convert to 1920x1080 (16:9)
   • FFmpeg command:
     ```
     ffmpeg -i vertical.mp4 \\
       -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" \\
       -c:v libx264 -c:a copy horizontal.mp4
     ```
   • Cache conversions (don't regenerate)

4. Caption Generation
   • Extract key points from script
   • Platform-specific tone:
     - YouTube: Educational + SEO keywords
     - TikTok: Casual + trending phrases
     - Instagram: Branded + emojis
     - LinkedIn: Professional + thought leadership
   • Auto-generate hashtags based on content
   • Emoji insertion (platform appropriate)

5. Hashtag Strategy
   • Scrape trending hashtags per platform
   • Mix strategy:
     - 30% high-volume (100k+ posts)
     - 50% medium-volume (10k-100k posts)
     - 20% niche (1k-10k posts)
   • Store hashtag performance data
   • Update strategy weekly

6. Publishing Queue
   • Batch upload approved videos
   • Schedule posts (best times per platform)
   • Stagger: Don't post all at once
   • Retry failed uploads (3 attempts)
   • Log all publishing activity
   • Send notification on success/failure

7. Error Handling
   • API rate limits: Respect and queue
   • Upload failures: Retry with exponential backoff
   • Invalid format: Re-convert and retry
   • Caption too long: Auto-truncate with "..."
   • Hashtag limit: Trim to platform max
   • Network errors: Queue for later

🔧 Technical Implementation:
• API: Publer REST API (Python SDK)
• Queue: Redis for publishing queue
• Scheduler: APScheduler or Celery Beat
• Storage: S3 for platform-specific videos
• Monitoring: Track success/failure rates

📁 File Structure:
backend/app/publer_service.py
backend/app/platform_formatter.py
backend/app/caption_generator.py
backend/app/hashtag_strategy.py
backend/app/publishing_queue.py
backend/app/video_converter.py

✅ Acceptance Criteria:
• Can post to all 5 platforms
• Platform-specific formatting applied
• Captions auto-generated correctly
• Hashtags relevant and trending
• LinkedIn video converted to 16:9
• Publishing queue processes in order
• Retry logic handles failures
• Success rate > 95%
• Can publish 10 videos in 10 minutes

📊 Estimated Effort: 16 hours (2 days)

🧪 Testing:
• Post test video to each platform
• Verify format on mobile devices
• Check captions render correctly
• Test hashtag clickability
• Simulate API failures
• Test rate limit handling
• Verify retry logic works
• Monitor for 48 hours""",
    milestone="M5: Publishing",
    status="Todo",
    owner="Codex",
    priority="High",
    eod_date=m5_start + timedelta(days=1),
    effort_hours=16,
    tags=["backend", "api", "social-media", "publishing"],
    acceptance_criteria="Posts to 5 platforms, formatting correct, captions generate, hashtags relevant, 95% success rate"
)

create_detailed_task(
    title="M5B: Analytics Dashboard - Performance Tracking System",
    summary="""Build comprehensive analytics dashboard for video performance

🎯 Goal: Track video performance across platforms and identify patterns

📋 Tasks:
1. Publer Analytics Integration
   • Fetch metrics via Publer API:
     - Views
     - Likes
     - Comments
     - Shares
     - Saves (Instagram/TikTok)
     - Engagement rate
     - Reach
     - Impressions
   • Schedule: Fetch every 6 hours
   • Store in PostgreSQL time-series table
   • Calculate 24hr, 7day, 30day trends

2. Dashboard UI (Frontend)

   A) Overview Section:
      • Total videos published (all-time)
      • Total views (all platforms combined)
      • Average engagement rate
      • Best performing video (this week)
      • Publishing velocity (videos/day)
      • Platform breakdown (pie chart)

   B) Performance Charts:
      • Line chart: Views over time (7/30/90 days)
      • Bar chart: Engagement by platform
      • Heatmap: Best posting times
      • Funnel: Approval → Published → Views

   C) Video Leaderboard:
      • Top 10 videos by views
      • Top 10 by engagement rate
      • Worst 5 performers (learn from failures)
      • Sortable table with filters

   D) Platform Comparison:
      • Side-by-side metrics per platform
      • Which platform drives most views?
      • Which has highest engagement?
      • ROI per platform (effort vs results)

   E) Retention Analysis:
      • YouTube: Retention curve (% watched)
      • Average watch time per video
      • Drop-off points (where users leave)
      • Identify ideal video length

   F) Audience Insights:
      • Demographics (age, gender, location)
      • Peak activity hours
      • Device breakdown (mobile vs desktop)
      • Traffic sources (browse, search, suggested)

3. Real-Time Monitoring
   • WebSocket connection for live updates
   • Notifications for milestone hits:
     - First 1K views
     - 10K views
     - 100K views
     - Viral threshold (1M views)
   • Alert on unusual patterns (sudden spike/drop)

4. Automated Reporting
   • Daily summary email (9 AM):
     - Yesterday's total views
     - Top performing video
     - Publishing schedule for today
   • Weekly digest (Monday morning):
     - Last 7 days performance
     - Week-over-week growth
     - Top 5 videos
     - Recommendations for next week
   • Monthly report (1st of month):
     - Full month metrics
     - Goal progress (views, engagement)
     - Cost analysis (API usage)
     - Strategic recommendations

5. Competitive Benchmarking
   • Track competitor accounts (public data)
   • Compare: Views, engagement, posting frequency
   • Identify: What works for them?
   • Alerts: When competitor goes viral (learn from it)

6. Export & Sharing
   • Export data: CSV, JSON, PDF
   • Share dashboard: Public link (read-only)
   • Embed charts: Iframe for Notion/Confluence
   • API access: GraphQL endpoint for custom queries

🔧 Technical Implementation:
• Frontend: Next.js + Recharts/Chart.js
• Backend: FastAPI + PostgreSQL
• Time-series: TimescaleDB extension
• Caching: Redis for dashboard data
• Real-time: WebSocket (Socket.io)
• Reporting: SendGrid for email

📁 File Structure:
frontend/app/analytics/page.tsx
frontend/components/AnalyticsOverview.tsx
frontend/components/PerformanceCharts.tsx
frontend/components/VideoLeaderboard.tsx
backend/app/analytics_service.py
backend/app/reporting.py
backend/app/metrics_aggregator.py

✅ Acceptance Criteria:
• Dashboard loads in < 2 seconds
• All charts render correctly
• Real-time updates work (test with mock data)
• Metrics match platform directly (verify accuracy)
• Daily email arrives on schedule
• Export functions work (CSV, PDF)
• Can track 100+ videos without slowdown
• Mobile responsive design

📊 Estimated Effort: 16 hours (2 days)

🧪 Testing:
• Load test with 500 videos
• Verify chart accuracy (manual comparison)
• Test real-time updates (simulate new views)
• Check email delivery
• Test export formats
• Mobile responsiveness check
• Accessibility audit (WCAG AA)""",
    milestone="M5: Publishing",
    status="Todo",
    owner="Claude",
    priority="High",
    eod_date=m5_start + timedelta(days=3),
    effort_hours=16,
    tags=["frontend", "analytics", "charts", "dashboard"],
    acceptance_criteria="Dashboard loads fast, charts accurate, real-time works, emails send, exports work, handles 100+ videos"
)

create_detailed_task(
    title="M5C: Learning Loop - Continuous Improvement System",
    summary="""Build ML system that learns from performance data

🎯 Goal: Automatically improve content strategy based on what works

📋 Tasks:
1. Data Collection Pipeline
   • Collect all video metadata:
     - Script (topic, keywords, structure)
     - Voice (speed, energy, voice type)
     - B-roll (clip types, timing)
     - Music (track, tempo)
     - Text overlays (style, frequency)
     - Duration (seconds)
     - Posting time (hour, day of week)
     - Platform
   • Collect performance metrics:
     - Views (1hr, 24hr, 7day, 30day)
     - Engagement rate
     - Watch time
     - Retention curve
     - Comments sentiment (positive/negative/neutral)
   • Store in structured format (JSON + DB)

2. Pattern Detection (ML)

   A) Script Analysis:
      • What topics get most views?
      • Ideal script length (word count)?
      • Hook patterns that work
      • CTA phrases with highest CTR
      • Keyword density correlation

   B) Voice Analysis:
      • Best voice for each topic
      • Optimal speaking speed (WPM)
      • Energy level vs engagement
      • Pause patterns and retention

   C) B-Roll Analysis:
      • Which clip types get most retention?
      • Optimal scene change frequency
      • Clip quality vs engagement
      • Best search keywords per topic

   D) Timing Analysis:
      • Best posting times per platform
      • Day of week performance
      • Optimal publishing frequency
      • Seasonal trends

   E) Format Analysis:
      • Ideal video duration
      • Text overlay frequency
      • Music tempo preference
      • Thumbnail style

3. Recommendation Engine
   Based on analysis, generate recommendations:

   • "AI news videos perform 2x better than crypto news"
     → Action: Prioritize AI topics in scraper

   • "Videos with 'Breaking:' in hook get 50% more views"
     → Action: Update script template to use "Breaking:"

   • "Voice speed at 160 WPM has best retention"
     → Action: Adjust TTS speed parameter

   • "Best posting time: Tuesday 9 AM EST"
     → Action: Schedule videos for Tuesdays

   • "TikTok performs 3x better than Instagram"
     → Action: Optimize for TikTok first

4. Automated Adjustments
   • Confidence threshold: Only apply if 80%+ confident
   • Gradual changes: A/B test before full rollout
   • Version control: Track what changed and why
   • Rollback: Revert if performance drops

   Example Auto-Adjustments:

   A) Script Template:
      • Update hook patterns
      • Adjust ideal word count
      • Add/remove CTA phrases
      • Modify keyword density

   B) Voice Settings:
      • Change default speed
      • Adjust energy level
      • Switch default voice

   C) B-Roll Strategy:
      • Update search keywords
      • Adjust scene change timing
      • Filter clip types

   D) Publishing Schedule:
      • Shift posting times
      • Change frequency
      • Prioritize platforms

5. A/B Testing Framework
   • Control group: Use current settings
   • Test group: Use recommended changes
   • Sample size: 20 videos per group
   • Duration: 7 days
   • Measure: Views, engagement, retention
   • Statistical significance: p < 0.05
   • Winner: Apply to all future videos

6. Performance Dashboard
   • Show learning progress over time
   • Display: Before/after metrics
   • Highlight: Successful adjustments
   • Flag: Failed experiments
   • Track: ROI of learning loop

   Metrics:
   • Baseline avg views: 10K
   • After 30 days: 15K (+50%)
   • After 60 days: 20K (+100%)
   • After 90 days: 25K (+150%)

7. Knowledge Base
   • Document all learnings
   • Create playbook:
     - "How to write viral hooks"
     - "Best B-roll for AI topics"
     - "Optimal posting schedule"
   • Share with team
   • Export as markdown for Notion

🔧 Technical Implementation:
• ML: Scikit-learn (classification, regression)
• Statistical analysis: SciPy (hypothesis testing)
• Visualization: Matplotlib + Seaborn
• Data: Pandas DataFrames
• Storage: PostgreSQL + S3 (raw data)
• Automation: Celery tasks (daily analysis)

📁 File Structure:
backend/app/ml/data_collector.py
backend/app/ml/pattern_detector.py
backend/app/ml/recommendation_engine.py
backend/app/ml/ab_testing.py
backend/app/ml/auto_adjuster.py
backend/app/ml/knowledge_base.py

✅ Acceptance Criteria:
• Collects data for 50+ videos
• Detects at least 5 patterns (statistically significant)
• Generates 10+ recommendations
• A/B tests 3 recommendations
• At least 1 recommendation improves performance
• Auto-applies winning changes
• Knowledge base generated
• Performance improves 10%+ over 30 days

📊 Estimated Effort: 8 hours (1 day)

🧪 Testing:
• Run analysis on 50 test videos
• Verify patterns are real (not spurious)
• Test recommendation logic
• Simulate A/B test results
• Check auto-adjustment safety
• Verify rollback works
• Measure improvement over time""",
    milestone="M5: Publishing",
    status="Todo",
    owner="Claude + Codex",
    priority="Medium",
    eod_date=m5_start + timedelta(days=4),
    effort_hours=8,
    tags=["ml", "analytics", "optimization", "backend"],
    acceptance_criteria="Collects data, detects patterns, generates recommendations, A/B tests, auto-applies, performance improves 10%+"
)

# ==========================================
# FINAL INTEGRATION TEST
# ==========================================
print("\n📋 FINAL MILESTONE: Integration & Launch")

create_detailed_task(
    title="M5D: End-to-End Integration Test - Full Automation",
    summary="""Test complete system running autonomously for 1 week

🎯 Goal: Prove system can operate 24/7 with zero manual intervention

📋 Test Scenarios:

1. Daily Automation Test (7 Days)

   Day 1:
   • System scrapes news at 6 AM
   • Generates 3 scripts by 7 AM
   • Creates 3 videos by 9 AM
   • All pass quality checks
   • Added to review queue
   • Human reviews and approves 2, rejects 1
   • 2 videos published at optimal times
   • Analytics update within 1 hour
   • Notion daily update posted

   Day 2-7:
   • Repeat same cycle
   • Test regeneration (at least 3 videos)
   • Test different topics (AI, crypto, tech)
   • Test all platforms (rotate)
   • Test feedback loop improvements
   • Test error recovery (simulate failures)

2. Error Handling Tests

   A) API Failures:
      • Gemini API down → Use cached templates
      • ElevenLabs down → Queue for retry
      • Artlist down → Use Pexels fallback
      • Publer down → Queue for later

   B) Content Issues:
      • No news articles found → Alert human
      • Script generation fails → Retry with simplified prompt
      • TTS fails → Try alternative voice
      • B-roll search returns 0 → Use stock fallback

   C) Quality Failures:
      • Video corruption → Regenerate
      • Audio sync off → Rebuild timeline
      • File size too large → Compress
      • Platform rejection → Reformat and resubmit

3. Performance Tests
   • Load: Generate 20 videos simultaneously
   • Speed: Full pipeline completes in < 30 min
   • Quality: 90%+ videos pass QC on first try
   • Approval: 80%+ videos approved by human
   • Publishing: 95%+ posts succeed
   • Analytics: Data accurate within 5%

4. Learning Tests
   • After 50 videos, identify 3 patterns
   • Test 1 recommendation via A/B test
   • Verify winning recommendation improves metrics
   • Check auto-adjustment applies correctly

5. Monitoring Tests
   • All logs captured
   • Errors trigger notifications
   • Daily summary email arrives
   • Notion updates post correctly
   • Dashboard shows real-time data

✅ Acceptance Criteria:
• System runs for 7 consecutive days
• Generates 4+ videos per day (28 total)
• 90%+ videos pass initial QC
• 80%+ videos approved
• 95%+ posts succeed
• Zero critical failures
• All errors handled gracefully
• Learning loop shows improvement
• Total human time < 30 min/day (just approvals)

📊 Estimated Effort: 8 hours setup + 7 days monitoring

🧪 Success Metrics:
• Uptime: 99.9%
• Video quality: 9/10 average
• Publishing success: 95%+
• Cost: < $100 for the week
• Engagement: Baseline established
• Improvements: 10%+ by end of week

📝 Deliverables:
• Test report with all metrics
• Error log with resolutions
• Performance benchmarks
• Recommendation for production
• Launch checklist""",
    milestone="M5: Publishing",
    status="Todo",
    owner="Claude + Codex + Gurvinder",
    priority="High",
    eod_date=m5_start + timedelta(days=7),
    effort_hours=8,
    tags=["testing", "integration", "launch", "automation"],
    acceptance_criteria="Runs 7 days, 28 videos, 90% QC pass, 80% approval, 95% publish, zero critical failures, <30 min/day human time"
)

print("\n"+"="*80)
print("✅ M4 & M5 COMPLETE WITH FULL DETAILS!")
print("="*80)
print("\n📊 Summary:")
print("  • M4: 3 detailed tasks (40 hours total)")
print("  • M5: 4 detailed tasks (48 hours total)")
print("  • All tasks include:")
print("    - Comprehensive task breakdown")
print("    - Technical implementation details")
print("    - File structures")
print("    - Acceptance criteria")
print("    - Testing procedures")
print("    - Effort estimates")
print("    - Tags for filtering")
print("\n🎯 Total structure now 100% complete!")
print("="*80)
