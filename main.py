import streamlit as st
import requests
import time

st.set_page_config(page_title="YT MP3 Downloader", layout="centered")
st.title("🎵 YouTube Playlist Downloader")

BACKEND_URL = "http://127.0.0.1:8000"

url = st.text_input("YouTube Playlist URL")
quality = st.selectbox("Select MP3 Quality (kbps)", ["320", "256", "192", "128"])

if st.button("🚀 Start Download"):
    if url:
        try:
            payload = {"url": str(url), "quality": str(quality)}
            requests.post(f"{BACKEND_URL}/start-download", json=payload)
            
            # Use a spinner instead of a progress bar
            with st.spinner("Processing your request..."):
                status_text = st.empty()
                
                while True:
                    res = requests.get(f"{BACKEND_URL}/progress").json()
                    status = res["status"]
                    p = res["percentage"]
                    
                    # Update status text so user sees which song is downloading
                    status_text.text(f"Current Status: {status} ({p}%)")
                    
                    if status == "ready":
                        break
                    
                    if "error" in status:
                        st.error(f"Error: {status}")
                        st.stop() # Stop execution if error occurs
                        
                    time.sleep(2)
            
            # Once the spinner finishes (status == "ready")
            st.success("✅ All songs processed and zipped!")
            zip_data = requests.get(f"{BACKEND_URL}/get-zip").content
            st.download_button(
                label="💾 Download ZIP Archive",
                data=zip_data,
                file_name="youtube_playlist.zip",
                mime="application/zip"
            )
            
        except Exception as e:
            st.error(f"Could not connect to backend: {e}")
    else:
        st.error("Please enter a URL")