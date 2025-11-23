FROM python:3.9-slim

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Setup App
WORKDIR /app
COPY . .

# Install Python Libs
RUN pip install --no-cache-dir -r requirements.txt

# Config Streamlit for Docker
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
