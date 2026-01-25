FROM python:3.11-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000
EXPOSE 7860

CMD uvicorn app:app --host 0.0.0.0 --port 8000 & streamlit run main.py --server.port 7860 --server.address 0.0.0.0