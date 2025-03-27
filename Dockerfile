# Gunakan image Python 3.12-slim sebagai base
FROM python:3.12-slim

# Tetapkan direktori kerja di dalam container
WORKDIR /app

# Copy requirements terlebih dahulu untuk caching
COPY requirements.txt /app/

# Buat virtual environment & install dependencies sebelum COPY semua file
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Salin seluruh isi proyek ke dalam container
COPY . /app

# Aktifkan virtual environment secara otomatis
ENV PATH="/opt/venv/bin:$PATH"

# Jalankan bot dengan interpreter Python dari virtual environment
CMD ["python", "main.py"]
