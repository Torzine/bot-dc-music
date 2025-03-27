RUN --mount=type=cache,id=s/f07f034e-2a6f-4d22-b41d-1573aeabcf2f-/root/cache/pip,target=/root/.cache/pip \
    python3 -m venv --copies /opt/venv && . /opt/venv/bin/activate && pip install -r requirements.txt
