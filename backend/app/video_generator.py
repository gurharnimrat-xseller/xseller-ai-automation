from __future__ import annotations

from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401
import os
import httpx
from typing import Dict, Any
from datetime import datetime

from sqlmodel import Session, select
from app.database import engine
from app.models import Post, Asset


# API Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
STOCKSTACK_API_KEY = os.getenv("STOCKSTACK_API_KEY", "")
ELEVENLABS_API_BASE = "https://api.elevenlabs.io/v1"
STOCKSTACK_API_BASE = "https://api.stockstack.com/v1"


async def generate_video_for_post(post: Post) -> Dict[str, Any]:
    """
    Generate a video for a post using:
    - StockStack: Get stock video clips
    - Eleven Labs: Generate voiceover
    - Combine them into final video
    """
    try:
        print(f"[video] Starting video generation for post {post.id}")
        
        # Step 1: Extract script sections
        script_sections = parse_video_script(post.body)
        
        # Step 2: Get stock video clips from StockStack
        video_clips = await get_stock_video_clips(script_sections, post.title)
        
        # Step 3: Generate voiceover with Eleven Labs
        voiceover_url = await generate_voiceover(script_sections["full_text"], post.title)
        
        # Step 4: Combine video and audio (simplified - in production use FFmpeg)
        # For now, we'll just save the video clip URL and voiceover URL
        # In production, you'd use FFmpeg or a video service to combine them
        
        # Step 5: Use the video clip (in production, combine with voiceover using FFmpeg)
        # For now, we'll use the stock video clip URL directly
        final_video_url = video_clips[0] if video_clips else "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
        
        # Step 6: Save video asset to database
        with Session(engine) as session:
            # Check if asset already exists (for regeneration)
            from sqlmodel import select
            existing_asset = session.exec(
                select(Asset).where(Asset.post_id == post.id, Asset.type == "video")
            ).first()
            
            if existing_asset:
                # Update existing asset
                existing_asset.path = final_video_url
                existing_asset.created_at = datetime.utcnow()
                video_asset = existing_asset
            else:
                # Create new asset entry
                video_asset = Asset(
                    post_id=post.id,
                    type="video",
                    path=final_video_url,
                    created_at=datetime.utcnow()
                )
                session.add(video_asset)
            
            # Update post status to approved (video is ready)
            db_post = session.get(Post, post.id)
            if db_post:
                db_post.status = "approved"  # Video is ready for review
                db_post.updated_at = datetime.utcnow()
            
            session.commit()
            session.refresh(video_asset)
        
        print(f"[video] Video generated successfully for post {post.id}, asset ID: {video_asset.id}, URL: {final_video_url}")
        
        return {
            "success": True,
            "video_url": final_video_url,
            "voiceover_url": voiceover_url,
            "asset_id": video_asset.id,
            "post_id": post.id,
        }
        
    except Exception as e:
        print(f"[video] Error generating video: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def parse_video_script(script: str) -> Dict[str, str]:
    """
    Parse video script into sections following the viral hook format:
    Hook (0-1.5s): ...
    Main (2-8s): ...
    Why (9-15s): ...
    CTA (16-20s): ...
    """
    sections = {
        "hook": "",
        "main": "",
        "why": "",
        "cta": "",
        "full_text": script
    }
    
    # Try to parse structured script with timing labels
    parts = script.split("\n")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        # Check for new format: "Hook (0-1.5s): ..." or "Hook: ..."
        if part.lower().startswith("hook"):
            # Handle both formats: "Hook (0-1.5s): text" and "Hook: text"
            if ":" in part:
                hook_text = part.split(":", 1)[1].strip()
                sections["hook"] = hook_text
            elif ")" in part:
                # Format: "Hook (0-1.5s) text" (no colon)
                hook_text = part.split(")", 1)[1].strip()
                sections["hook"] = hook_text
        elif part.lower().startswith("main"):
            if ":" in part:
                main_text = part.split(":", 1)[1].strip()
                sections["main"] = main_text
            elif ")" in part:
                main_text = part.split(")", 1)[1].strip()
                sections["main"] = main_text
        elif part.lower().startswith("why"):
            if ":" in part:
                why_text = part.split(":", 1)[1].strip()
                sections["why"] = why_text
            elif ")" in part:
                why_text = part.split(")", 1)[1].strip()
                sections["why"] = why_text
        elif part.lower().startswith("cta"):
            if ":" in part:
                cta_text = part.split(":", 1)[1].strip()
                sections["cta"] = cta_text
            elif ")" in part:
                cta_text = part.split(")", 1)[1].strip()
                sections["cta"] = cta_text
    
    # Combine all sections for full text (in order: Hook, Main, Why, CTA)
    full_text_parts = []
    if sections["hook"]:
        full_text_parts.append(sections["hook"])
    if sections["main"]:
        full_text_parts.append(sections["main"])
    if sections["why"]:
        full_text_parts.append(sections["why"])
    if sections["cta"]:
        full_text_parts.append(sections["cta"])
    
    full_text = " ".join(full_text_parts).strip()
    if not full_text:
        full_text = script
    
    sections["full_text"] = full_text
    
    print(f"[video] Parsed script sections - Hook: {len(sections['hook'])} chars, Main: {len(sections['main'])} chars, Why: {len(sections['why'])} chars, CTA: {len(sections['cta'])} chars")
    
    return sections


async def get_stock_video_clips(script_sections: Dict[str, str], title: str) -> list[str]:
    """Get stock video clips from StockStack API."""
    if not STOCKSTACK_API_KEY:
        print("[video] StockStack API key not configured, using placeholder video")
        # Return a working sample video URL
        return ["https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"]
    
    try:
        # Extract keywords from title and script for better search
        keywords = title.split()[:5]  # First 5 words
        search_query = " ".join(keywords)
        
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {STOCKSTACK_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Try different possible API endpoints
            endpoints = [
                f"{STOCKSTACK_API_BASE}/search",
                f"{STOCKSTACK_API_BASE}/videos/search",
                f"{STOCKSTACK_API_BASE}/assets/search",
            ]
            
            video_urls = []
            
            for endpoint in endpoints:
                try:
                    response = await client.get(
                        endpoint,
                        headers=headers,
                        params={
                            "q": search_query,
                            "query": search_query,
                            "type": "video",
                            "per_page": 3,
                            "limit": 3,
                        },
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        # Try different response formats
                        videos = (
                            data.get("videos", []) or 
                            data.get("results", []) or
                            data.get("data", []) or
                            data.get("items", [])
                        )
                        
                        if videos and isinstance(videos, list):
                            for video in videos[:3]:
                                url = (
                                    video.get("url") or 
                                    video.get("video_url") or 
                                    video.get("preview_url") or
                                    video.get("mp4") or
                                    video.get("hd") or
                                    video.get("source")
                                )
                                if url and url.startswith("http"):
                                    video_urls.append(url)
                        
                        if video_urls:
                            print(f"[video] Found {len(video_urls)} stock videos from {endpoint}")
                            break
                            
                except Exception as e:
                    print(f"[video] Error with endpoint {endpoint}: {str(e)}")
                    continue
            
            if video_urls:
                return video_urls
            
            print("[video] No videos found from StockStack, using placeholder")
            return ["https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"]
            
    except Exception as e:
        print(f"[video] Error fetching stock videos: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return placeholder
        return ["https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"]


async def generate_voiceover(script_text: str, title: str) -> str:
    """Generate voiceover using Eleven Labs API and save to file."""
    if not ELEVENLABS_API_KEY:
        print("[video] Eleven Labs API key not configured, skipping voiceover")
        return ""
    
    try:
        # Clean and prepare text (limit to reasonable length for voiceover)
        text = script_text[:1000]  # Limit to reasonable length
        if not text.strip():
            text = title  # Fallback to title if script is empty
        
        async with httpx.AsyncClient() as client:
            headers = {
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            }
            
            # Use default voice (Rachel) or you can get available voices from /voices endpoint
            voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default voice (Rachel)
            
            # Generate speech
            url = f"{ELEVENLABS_API_BASE}/text-to-speech/{voice_id}"
            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            
            response = await client.post(
                url,
                headers=headers,
                json=payload,
                timeout=60.0
            )
            
            if response.status_code == 200:
                # Save audio file to disk (in production, upload to S3/cloud storage)
                import os
                os.makedirs("/tmp/xseller_audio", exist_ok=True)
                
                audio_filename = f"voiceover_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp3"
                audio_path = f"/tmp/xseller_audio/{audio_filename}"
                
                # Write audio data to file
                with open(audio_path, "wb") as f:
                    f.write(response.content)
                
                print(f"[video] Voiceover saved to {audio_path}")
                
                # In production, upload to cloud storage and return public URL
                # For now, return the file path (would need to serve it or upload to CDN)
                # Return a placeholder that indicates voiceover was generated
                return f"file://{audio_path}"  # Local file path - in production use CDN URL
                
            else:
                error_text = response.text
                print(f"[video] Eleven Labs API error {response.status_code}: {error_text}")
                return ""
                
    except Exception as e:
        print(f"[video] Error generating voiceover: {str(e)}")
        import traceback
        traceback.print_exc()
        return ""


async def process_video_generation_queue():
    """Process all posts with status 'video_production'."""
    print("[video] Processing video generation queue...")
    with Session(engine) as session:
        stmt = select(Post).where(
            Post.kind == "video",
            Post.status == "video_production",
            Post.deleted_at.is_(None)
        )
        posts = session.exec(stmt).all()
        
        print(f"[video] Found {len(posts)} videos to generate")
        
        for post in posts:
            try:
                print(f"[video] Generating video for post {post.id}...")
                await generate_video_for_post(post)
            except Exception as e:
                print(f"[video] Failed to generate video for post {post.id}: {str(e)}")
                import traceback
                traceback.print_exc()
                # Update status to failed
                db_post = session.get(Post, post.id)
                if db_post:
                    db_post.status = "failed"
                    session.add(db_post)
                    session.commit()

