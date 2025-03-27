# Gunakan image Python 3.12-slim sebagai base
FROM python:3.12-slim

# (Opsional) Set environment variable
ENV NIXPACKS_PATH=/opt/venv/bin:$NIXPACKS_PATH

# Tentukan direktori kerja
WORKDIR /app

# Salin seluruh file proyek ke container
COPY . /app

# Buat virtual environment & install dependencies TANPA cache mount
RUN python3 -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --no-cache-dir -r requirements.txt

# Jalankan bot
CMD ["python3", "main.py"]
