from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yt_dlp
import os
import shutil
import zipfile
import re
import gc
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    file_format: str 

def progress_hook(d):
    if d['status'] == 'downloading':
        # This keeps the text updated in the UI
        progress_db["status"] = (
            f"Downloading {progress_db['current_item']} of {progress_db['total_items']}"
        )

def download_logic(url, quality, file_format):
    try:
        download_path = "downloads"
        zip_name = "playlist.zip"

        # 1. CLEANUP
        if os.path.exists(download_path): shutil.rmtree(download_path)
        if os.path.exists(zip_name): os.remove(zip_name)
        os.makedirs(download_path)

        # 2. ANALYZE
        with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            entries = info.get('entries', [info])
            progress_db["total_items"] = len(entries)

        # 3. OPTIONS
        ydl_opts = {
            'outtmpl': f'{download_path}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'ignoreerrors': True,
        }

        if file_format == "mp3":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality,
                }],
            })
        else:
            height = quality.replace("p", "")
            ydl_opts.update({
                'format': f'bestvideo[height<={height}]+bestaudio/best',
                'merge_output_format': 'mp4',
            })

        # 4. DOWNLOAD LOOP
        for i, entry in enumerate(entries, 1):
            progress_db["current_item"] = i
            
            # This line FIXES the progress bar visibility
            progress_db["percentage"] = int((i / progress_db["total_items"]) * 95)
            
            video_url = entry.get('url') or entry.get('webpage_url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            gc.collect()

        # 5. ZIP
        progress_db["status"] = "Creating ZIP..."
        with zipfile.ZipFile(zip_name, "w") as zipf:
            for root, _, files in os.walk(download_path):
                for file in files:
                    zipf.write(os.path.join(root, file), file)
        
        shutil.rmtree(download_path)
        
        progress_db["percentage"] = 100
        progress_db["status"] = "ready"
        progress_db["is_downloading"] = False

    except Exception as e:
        print(f"Error: {e}")
        progress_db["status"] = f"error: {str(e)}"
        progress_db["is_downloading"] = False

@app.post("/start-download")
async def start_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    progress_db.update({
        "percentage": 0, "current_item": 0, 
        "total_items": 1, "status": "Initializing...", "is_downloading": True
    })
    background_tasks.add_task(download_logic, request.url, request.quality, request.file_format)
    return {"message": "Started"}

@app.get("/progress")
async def get_progress():
    return progress_db

@app.get("/get-zip")
async def get_zip():
    return FileResponse("playlist.zip", media_type="application/zip", filename="playlist.zip")