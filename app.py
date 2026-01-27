from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yt_dlp
import os
import shutil
import zipfile
import re
import gc

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
    file_format: str 

def clean_percent(p_str):
    clean = re.sub(r'\x1b\[[0-9;]*m', '', p_str)
    return clean.replace('%', '').strip()

def progress_hook(d):
    if d['status'] == 'downloading':
        progress_db["status"] = (
            f"Downloading {progress_db['current_item']} / "
            f"{progress_db['total_items']}"
        )

def download_logic(url, quality, file_format):
    try:
        download_path = "downloads"
        zip_name = "playlist.zip"

        # Cleanup existing files to save disk space
        if os.path.exists(download_path): shutil.rmtree(download_path)
        if os.path.exists(zip_name): os.remove(zip_name)
        os.makedirs(download_path)

        # 1. Analyze playlist
        with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True, 'ignoreerrors': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise Exception("Could not retrieve playlist info.")
            
            entries = [e for e in info.get('entries', []) if e is not None]
            if not entries: 
                entries = [info]
            
            progress_db["total_items"] = len(entries)

        # 2. Configure ydl_opts with Memory Protections
        ydl_opts = {
            'outtmpl': f'{download_path}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'ignoreerrors': True,
            'buffersize': 1024 * 16, # Small buffer forces data to Disk, saving RAM
            'noprogress': True,      # Reduces CPU usage for logging
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
            # Your modified height logic
            height = int(quality.replace("p", ""))
            ydl_opts.update({
                'format': f'bestvideo[ext=mp4][height<={height}]+bestaudio[ext=m4a]/best[ext=mp4][height<={height}]/best',
                'merge_output_format': 'mp4',
                'skip_unavailable_fragments': True,
                'cookiefile': 'cookies.txt' # Ensure this file exists in your directory
            })

        # 3. Download loop with RAM clearing
        for i, entry in enumerate(entries, 1):
            progress_db["current_item"] = i
            progress_db["status"] = f"Downloading video {i} out of {progress_db['total_items']}..."
            
            video_url = entry.get('url') or entry.get('webpage_url') or f"https://www.youtube.com/watch?v={entry['id']}"
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            # CRUCIAL: Manually clear RAM after every video
            gc.collect()

        # 4. Finalizing
        progress_db["status"] = "Finalizing: Zipping files..."
        # Using ZIP_DEFLATED ensures compression happens on disk
        with zipfile.ZipFile(zip_name, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(download_path):
                for file in files:
                    if file.endswith((".mp3", ".mp4")):
                        zipf.write(os.path.join(root, file), file)
        
        # Cleanup folder immediately after zipping
        shutil.rmtree(download_path)
        
        progress_db["percentage"] = 100
        progress_db["status"] = "ready"
        progress_db["is_downloading"] = False

    except Exception as e:
        progress_db["status"] = f"error: {str(e)}"
        progress_db["is_downloading"] = False

@app.post("/start-download")
async def start_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    progress_db.update({
        "percentage": 0, "current_item": 0, "total_items": 1,
        "status": "Analyzing playlist...", "is_downloading": True
    })
    # Pass the format to the logic
    background_tasks.add_task(download_logic, request.url, request.quality, request.file_format)
    return {"message": "Started"}

@app.get("/progress")
async def get_progress():
    return progress_db

@app.get("/get-zip")
async def get_zip():
    return FileResponse("playlist.zip", media_type="application/zip", filename="playlist.zip")