from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yt_dlp
import os
import shutil
import zipfile
import gc
from fastapi.middleware.cors import CORSMiddleware
import static_ffmpeg

# Initialize FFmpeg
static_ffmpeg.add_paths()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vercel requires writing to /tmp
TMP_DOWNLOAD_PATH = "/tmp/downloads"
TMP_ZIP_NAME = "/tmp/playlist.zip"

progress_db = {
    "percentage": 0, 
    "status": "idle",
    "current_item": 0,
    "total_items": 1,
    "is_downloading": False
}

class DownloadRequest(BaseModel):
    url: str
    quality: str
    file_format: str 

def progress_hook(d):
    if d['status'] == 'downloading':
        progress_db["status"] = (
            f"Downloading {progress_db['current_item']} of {progress_db['total_items']}"
        )

def download_logic(url, quality, file_format):
    try:
        # 1. CLEANUP (Using /tmp paths)
        if os.path.exists(TMP_DOWNLOAD_PATH): shutil.rmtree(TMP_DOWNLOAD_PATH)
        if os.path.exists(TMP_ZIP_NAME): os.remove(TMP_ZIP_NAME)
        os.makedirs(TMP_DOWNLOAD_PATH, exist_ok=True)

        # 2. ANALYZE
        with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            entries = info.get('entries', [info])
            progress_db["total_items"] = len(entries)

        # 3. OPTIONS
        ydl_opts = {
            'outtmpl': f'{TMP_DOWNLOAD_PATH}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'ignoreerrors': True,
            'nocheckcertificate': True, # Useful for server environments
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
            progress_db["percentage"] = int((i / progress_db["total_items"]) * 95)
            
            video_url = entry.get('url') or entry.get('webpage_url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            gc.collect()

        # 5. ZIP
        progress_db["status"] = "Creating ZIP..."
        with zipfile.ZipFile(TMP_ZIP_NAME, "w") as zipf:
            for root, _, files in os.walk(TMP_DOWNLOAD_PATH):
                for file in files:
                    zipf.write(os.path.join(root, file), file)
        
        if os.path.exists(TMP_DOWNLOAD_PATH):
            shutil.rmtree(TMP_DOWNLOAD_PATH)
        
        progress_db["percentage"] = 100
        progress_db["status"] = "ready"
        progress_db["is_downloading"] = False

    except Exception as e:
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
    if os.path.exists(TMP_ZIP_NAME):
        return FileResponse(TMP_ZIP_NAME, media_type="application/zip", filename="playlist.zip")
    raise HTTPException(status_code=404, detail="File not found")