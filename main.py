import streamlit as st
import requests
import time
import threading
import uvicorn
from app import app 

# --- BACKEND INTEGRATION ---
def run_backend():
    # Use 127.0.0.1 for better compatibility in cloud containers
    uvicorn.run(app, host="127.0.0.1", port=8000)

if "backend_started" not in st.session_state:
    thread = threading.Thread(target=run_backend, daemon=True)
    thread.start()
    st.session_state["backend_started"] = True
    # Give the backend a moment to initialize before the user interacts
    time.sleep(1) 

# --- UI SETUP ---
st.set_page_config(page_title="YouTube Downloader", layout="wide", page_icon="📥")
st.title("YouTube Playlist Downloader 📥")

url = st.text_input("Enter YouTube URL (Video or Playlist):", placeholder="https://www.youtube.com/playlist?list=...")

col1, col2 = st.columns(2)

with col1:
    download_type = st.radio("Select Format:", ("MP3 (Audio)", "MP4 (Video)"))

with col2:
    if "MP3" in download_type:
        quality = st.selectbox("Select Audio Bitrate (kbps):", ("192", "128", "320"))
    else:
        quality = st.selectbox("Select Max Resolution:", ("720p", "1080p", "480p", "360p"))

# --- DOWNLOAD LOGIC ---
if st.button("Start Download"):
    if url:
        fmt = "mp3" if "MP3" in download_type else "mp4"
        payload = {"url": url, "quality": quality, "file_format": fmt}
        
        try:
            # We use 127.0.0.1 to match the backend host
            requests.post("http://127.0.0.1:8000/start-download", json=payload)
            
            bar = st.progress(0)
            status_display = st.empty()
            
            while True:
                response = requests.get("http://127.0.0.1:8000/progress")
                if response.status_code == 200:
                    prog = response.json()
                    bar.progress(prog["percentage"] / 100)
                    status_display.info(f"✨ Status: {prog['status']}")
                    
                    if prog["status"] == "ready":
                        st.success("✅ Download Complete! Your file is ready.")
                        with open("playlist.zip", "rb") as f:
                            st.download_button(
                                label="💾 Download ZIP",
                                data=f,
                                file_name="youtube_playlist.zip",
                                mime="application/zip"
                            )
                        break
                    elif "error" in prog["status"]:
                        st.error(f"❌ {prog['status']}")
                        break
                time.sleep(1) # Slightly longer sleep reduces CPU load on the server
        except Exception as e:
            st.error(f"Could not connect to backend: {e}")
    else:
        st.warning("⚠️ Please enter a valid YouTube URL.")

# --- FOOTER ---
st.markdown("---")
st.caption("Note: Large playlists may take a few minutes to process. Please don't refresh the page.")