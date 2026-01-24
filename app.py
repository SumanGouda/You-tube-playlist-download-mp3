from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yt_dlp
import os
import shutil
import zipfile
import re

app = FastAPI()

# Initial State
INITIAL_STATE = {
    "percentage": 0, 
    "status": "idle",
    "current_item": 0,
    "total_items": 1,
    "is_downloading": False
}

progress_db = INITIAL_STATE.copy()

class DownloadRequest(BaseModel):
    url: str
    quality: str

def clean_percent(p_str):
    clean = re.sub(r'\x1b\[[0-9;]*m', '', p_str)
    return clean.replace('%', '').strip()

def progress_hook(d):
    if d['status'] == 'downloading':
        p_str = d.get('_percent_str', '0%')
        try:
            song_p = float(clean_percent(p_str))
            
            # Weighted Math
            completed_weight = (progress_db["current_item"] - 1) * 100
            total_weighted_p = (completed_weight + song_p) / progress_db["total_items"]
            
            # Crucial: Never let the percentage go backward
            new_p = round(total_weighted_p, 2)
            if new_p > progress_db["percentage"]:
                progress_db["percentage"] = new_p
                
            progress_db["status"] = f"Downloading song {progress_db['current_item']} of {progress_db['total_items']}"
        except:
            pass

def download_logic(url, quality):
    try:
        download_path = "downloads"
        zip_name = "playlist.zip"

        if os.path.exists(download_path):
            shutil.rmtree(download_path)
        if os.path.exists(zip_name):
            os.remove(zip_name)
        os.makedirs(download_path)

        with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            entries = info.get('entries', [info])
            progress_db["total_items"] = len(entries)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{download_path}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
        }

        for i, entry in enumerate(entries, 1):
            progress_db["current_item"] = i
            # Force the status text to update so the user knows a new song started
            progress_db["status"] = f"Starting song {i} of {len(entries)}..."
            
            video_url = entry.get('url') or entry.get('webpage_url') or f"https://www.youtube.com/watch?v={entry['id']}"
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

        progress_db["status"] = "Zipping files..."
        with zipfile.ZipFile(zip_name, "w") as zipf:
            for root, dirs, files in os.walk(download_path):
                for file in files:
                    if file.endswith(".mp3"):
                        zipf.write(os.path.join(root, file), file)
        
        shutil.rmtree(download_path) # Delete the folder of individual MP3s
        
        progress_db["percentage"] = 100
        progress_db["status"] = "ready"
        progress_db["is_downloading"] = False
    except Exception as e:
        progress_db["status"] = f"error: {str(e)}"
        progress_db["is_downloading"] = False

@app.post("/start-download")
async def start_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    # Reset State Completely
    progress_db.update({
        "percentage": 0,
        "current_item": 0,
        "total_items": 1,
        "status": "Analyzing playlist...",
        "is_downloading": True
    })
    background_tasks.add_task(download_logic, request.url, request.quality)
    return {"message": "Started"}

@app.get("/progress")
async def get_progress():
    return progress_db

@app.get("/get-zip")
async def get_zip():
    return FileResponse("playlist.zip", media_type="application/zip", filename="playlist.zip")