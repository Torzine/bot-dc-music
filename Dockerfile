--mount=type=cache,id=cache-s_f07f034e-2a6f-4d22-b41d-1573aeabcf2f,target=/root/.cache/pip \
    python3 -m venv --copies /opt/venv && . /opt/venv/bin/activate && pip install -r requirements.txt

# Tahap 1: Gunakan image Python 3.12-slim sebagai base image
FROM python:3.12-slim

# Atur environment variable jika diperlukan
ENV NIXPACKS_PATH=/opt/venv/bin:$NIXPACKS_PATH

# Tentukan direktori kerja di dalam container
WORKDIR /app

# Salin seluruh file proyek ke dalam container
COPY . /app

# Buat virtual environment dan install dependensi
RUN --mount=type=cache,id=cache_pip,target=/root/.cache/pip \
    python3 -m venv --copies /opt/venv && . /opt/venv/bin/activate && pip install -r requirements.txt

# Perintah untuk menjalankan bot ketika container mulai
CMD ["python3", "main.py"]
