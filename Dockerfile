FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# CPU-only torch/torchaudio (smaller wheels than the default index)
ARG TORCH_VERSION=2.5.1
RUN pip install --no-cache-dir \
        torch==${TORCH_VERSION} \
        torchaudio==${TORCH_VERSION} \
        --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Preload the v5_ru model so it is baked into the image (fast cold start).
RUN python -c "from silero import silero_tts; silero_tts(language='ru', speaker='v5_ru')"

EXPOSE 5001

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5001"]
