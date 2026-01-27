import streamlit as st
import requests
import time
import threading
import uvicorn
from app import app  # Import your FastAPI app object

def run_backend():
    # Runs the FastAPI server on a background thread
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Start the thread only once
if "backend_started" not in st.session_state:
    thread = threading.Thread(target=run_backend, daemon=True)
    thread.start()
    st.session_state["backend_started"] = True

st.set_page_config(page_title="YouTube Downloader", layout="wide")
st.title("YouTube Playlist Downloader 📥")

url = st.text_input("Enter YouTube URL (Video or Playlist):")
col1, col2 = st.columns(2)

with col1:
    download_type = st.radio("Select Format:", ("MP3 (Audio)", "MP4 (Video)"))

with col2:
    if "MP3" in download_type:
        quality = st.selectbox("Select Audio Bitrate (kbps):", ("192", "128", "320"))
    else:
        quality = st.selectbox("Select Max Resolution:", ("720p", "1080p", "480p", "360p"))

if st.button("Start Download"):
    if url:
        fmt = "mp3" if "MP3" in download_type else "mp4"
        payload = {"url": url, "quality": quality, "file_format": fmt}
        
        requests.post("http://localhost:8000/start-download", json=payload)
        
        bar = st.progress(0)
        status_display = st.empty()
        
        while True:
            prog = requests.get("http://localhost:8000/progress").json()
            bar.progress(prog["percentage"] / 100)
            status_display.info(f"✨ {prog['status']}")
            
            if prog["status"] == "ready":
                st.success("Download Complete! Your file is ready.")
                with open("playlist.zip", "rb") as f:
                    st.download_button("💾 Download ZIP", f, file_name="youtube_playlist.zip")
                break
            elif "error" in prog["status"]:
                st.error(prog["status"])
                break
            time.sleep(0.5)
    else:
        st.warning("Please enter a valid YouTube URL.")