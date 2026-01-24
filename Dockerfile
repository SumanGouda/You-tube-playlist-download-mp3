# 1. Use an official Python runtime as a parent image
FROM python:3.11-slim


# 2. Install FFmpeg (Crucial for MP3 conversion)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 3. Set the working directory in the container
WORKDIR /app

# 4. Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code
COPY . .

# 6. Expose the ports for FastAPI (8000) and Streamlit (7860)
EXPOSE 8000
EXPOSE 7860

# 7. Start both servers using a single command
# uvicorn runs the backend in the background (&)
# streamlit runs the frontend in the foreground
CMD uvicorn app:app --host 0.0.0.0 --port 8000 & streamlit run main.py --server.port 7860 --server.address 0.0.0.0