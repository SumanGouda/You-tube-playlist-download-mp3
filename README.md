# 🎵 YouTube Playlist to MP3 Downloader

A robust Python-based automation tool that downloads entire YouTube playlists and converts them into high-quality MP3 files. Designed for desktop users who want an organized, local music library with zero manual effort.

---

## 🚀 Key Features

* **Batch Processing:** Download 100+ songs from a single playlist link or a list of links.
* **High-Fidelity Audio:** Automatically extracts the best available audio and converts it to **320kbps MP3**.
* **Smart Organization:** Files are automatically named using the `%(title)s` format to keep your library clean.
* **Session Persistence:** Uses `cookies.txt` to bypass authentication hurdles and prevent "403 Forbidden" errors.
* **Performance:** Optimized using `yt-dlp`, the gold standard for media extraction.

## 🛠️ Tech Stack

* **Language:** Python 3.x
* **Interface:** Jupyter Notebook (`.ipynb`)
* **Core Library:** `yt-dlp`
* **Processing Engine:** `FFmpeg` (for high-quality audio conversion)

---

## 📋 Prerequisites

Before running the notebook, ensure you have the following installed:

1.  **FFmpeg:** Essential for the MP3 conversion process.
    ```bash
    # Windows (via Chocolatey)
    choco install ffmpeg
    ```
2.  **yt-dlp:** Included in the requirements file.

---

## ⚙️ Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/SumanGouda/You-tube-playlist-download-mp3.git](https://github.com/SumanGouda/You-tube-playlist-download-mp3.git)
   cd You-tube-playlist-download-mp3

2. **Install Requirements**
    ```bash
    pip install requirements.txt