# Gunakan image Python 3.12-slim sebagai base image
FROM python:3.12-slim

# Tetapkan direktori kerja di dalam container
WORKDIR /app

# Salin seluruh isi proyek ke dalam container
COPY . /app

# Buat virtual environment di /opt/venv dan install dependensi
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Jalankan bot dengan interpreter Python dari virtual environment
CMD ["/opt/venv/bin/python", "main.py"]
