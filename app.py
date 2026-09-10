import io
import logging
import os
import re
import wave

import numpy as np
import torch
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

SPEAKERS = ("aidar", "baya", "kseniya", "xenia", "eugene")

DEFAULT_VOICE = os.getenv("TTS_DEFAULT_VOICE", "xenia")
SAMPLE_RATE = int(os.getenv("TTS_SAMPLE_RATE", "48000"))
NUM_THREADS = int(os.getenv("TTS_NUM_THREADS", "0"))
TRANSLIT = os.getenv("TTS_TRANSLIT", "0").lower() in ("1", "true", "yes", "on")

if NUM_THREADS > 0:
    torch.set_num_threads(NUM_THREADS)

logger = logging.getLogger("silero-tts")
logging.basicConfig(level=logging.INFO)

from silero import silero_tts
from translit import transliterate_latin

model, _ = silero_tts(language="ru", speaker="v5_ru")

app = FastAPI(title="Silero TTS v5")


class SpeakRequest(BaseModel):
    text: str
    voice: str = ""


def render_wav(tensor: torch.Tensor, sample_rate: int) -> bytes:
    audio = np.asarray(tensor.detach().cpu().numpy()).reshape(-1)
    audio = np.clip(audio, -1.0, 1.0)
    pcm = (audio * 32767.0).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(pcm.tobytes())
    return buf.getvalue()


@app.get("/health")
@app.get("/healthprobe")
def health():
    return {"ok": True}


@app.post("/speak")
def speak(req: SpeakRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="empty text")

    logger.info("speak in : %r", req.text)
    if TRANSLIT:
        text = transliterate_latin(text)
        logger.info("speak out: %r", text)

    speaker = req.voice.strip() or DEFAULT_VOICE
    fell_back = speaker not in SPEAKERS
    used = speaker if not fell_back else DEFAULT_VOICE

    try:
        audio = model.apply_tts(
            text=text,
            speaker=used,
            sample_rate=SAMPLE_RATE,
            put_accent=True,
            put_yo=True,
            put_stress_homo=True,
            put_yo_homo=True,
        )
    except Exception as exc:
        logger.exception("apply_tts failed")
        if isinstance(exc, ValueError) and not re.search(r"[а-яА-ЯёЁ]", text):
            raise HTTPException(
                status_code=422,
                detail="text contains no Cyrillic; this engine is Russian-only",
            ) from exc
        raise HTTPException(
            status_code=500, detail=f"{type(exc).__name__}: {exc}"
        ) from exc

    wav = render_wav(audio, SAMPLE_RATE)

    headers = {}
    if fell_back:
        headers["X-TTS-Fell-Back"] = "true"
        headers["X-TTS-Voice-Used"] = used
        headers["X-TTS-Fell-Back-Reason"] = f"unknown voice '{speaker}'"

    return Response(content=wav, media_type="audio/wav", headers=headers)
