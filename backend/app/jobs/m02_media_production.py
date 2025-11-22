import os
import time
import requests
from sqlmodel import Session,  select
from app.database import engine
from app.models import Article

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
TEST_MODE = os.getenv('TEST_MODE', 'false').lower() == 'true'

def generate_voice(script: str, retries=3) -> str:
    """Generate voice using ElevenLabs Rachel voice"""
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"  # Rachel voice
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": script[:2500],  # Limit to prevent too long audio
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    for attempt in range(retries):
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Save audio temporarily
            audio_path = f"/tmp/voice_{int(time.time())}.mp3"
            with open(audio_path, 'wb') as f:
                f.write(response.content)
            
            # TODO: Upload to Railway volume or S3
            # For now, return local path (replace with actual upload)
            return audio_path
            
        except Exception as e:
            print(f"ElevenLabs attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise

def search_broll(keywords: str, retries=3) -> str:
    """Search Pexels for relevant B-roll footage"""
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": keywords,
        "per_page": 5,
        "orientation": "portrait",  # For 9:16 vertical videos
        "size": "medium"
    }
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('videos'):
                print(f"No videos found for keywords: {keywords}")
                return None
            
            # Get highest quality vertical video
            video = data['videos'][0]
            video_files = video['video_files']
            
            # Find best vertical video file
            for vf in video_files:
                if vf.get('width', 0) <= 1080 and vf.get('height', 0) >= 1920:
                    return vf['link']
            
            # Fallback to first available
            return video_files[0]['link']
            
        except Exception as e:
            print(f"Pexels attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise

def run_m02_job():
    with Session(engine) as session:
        # Fetch articles needing media
        articles = session.execute(
            select(Article)
            .where(Article.is_test == TEST_MODE)
            .where(Article.status == "scripted")
            .where(Article.voice_url == None)
            .limit(5)
        ).scalars().all()
        
        print(f"Processing {len(articles)} articles for M02")
        
        for article in articles:
            try:
                print(f"Processing article {article.id}: {article.title[:50]}...")
                
                # Generate voice
                article.voice_url = generate_voice(article.script)
                print(f"  ✅ Voice generated")
                
                # Extract keywords from title for B-roll search
                keywords = " ".join(article.title.split()[:4])
                article.broll_video_url = search_broll(keywords)
                print(f"  ✅ B-roll found: {keywords}")
                
                session.commit()
                print(f"✅ Article {article.id} media ready")
                
            except Exception as e:
                print(f"❌ Article {article.id} failed: {e}")
                session.rollback()
                continue

if __name__ == "__main__":
    run_m02_job()
