# 🎵 YouTube Playlist to MP3 Downloader

A robust Python-based automation tool that downloads entire YouTube playlists and converts them into high-quality MP3 files. Designed for desktop users who want an organized, local music library with zero manual effort.



---

## 🚀 Key Features

* **Batch Processing:** Download 100+ songs from a single playlist link.
* **High-Fidelity Audio:** Automatically extracts the best available audio and converts it to **320kbps MP3**.
* **Smart Organization:** Files are automatically named using the `%(title)s` format to keep your library clean.
* **Error Handling:** Built-in logic to handle common YouTube hurdles like "Permission Denied" and missing formats.
* **Performance:** Optimized using `yt-dlp`, the gold standard for media extraction.

## 🛠️ Tech Stack

* **Language:** Python 3.x
* **Core Library:** `yt-dlp`
* **Processing Engine:** `FFmpeg` (for high-quality audio conversion)
* **Environment:** Desktop / CLI

---

## 📋 Prerequisites

Before running the script, ensure you have the following installed:

1.  **Python 3.x**
2.  **FFmpeg:** Essential for the MP3 conversion process.
    ```bash
    # On Windows (via Chocolatey)
    choco install ffmpeg
    ```
3.  **yt-dlp:**
    ```bash
    pip install yt-dlp
    ```

## ⚙️ Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SumanGouda/youtube-playlist-downloader.git
   cd youtube-playlist-downloader

2. **Install Dependencies**
    ```bash
    pip install -r requirements.txt