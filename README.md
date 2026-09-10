# Silero TTS v5 — self-hosted эндпоинт для SUB/WAVE

Локальный TTS-сервер на [Silero v5](https://github.com/snakers4/silero-models) (русский),
реализующий контракт движка **Remote** из SUB/WAVE:

- `GET /health` (и `/healthprobe`) → `{"ok": true}`
- `POST /speak` `{"text": "...", "voice": "..."}` → `200` + WAV в теле ответа

Голоса: `aidar`, `baya`, `kseniya`, `xenia`, `eugene`. Включены флаги
автоударений и омографов (`put_accent`, `put_yo`, `put_stress_homo`, `put_yo_homo`).

## Запуск

```bash
cd silero
cp .env.example .env    # при необходимости поправь порт/голос
docker compose up -d --build
```

Первый build скачивает модель (~140 МБ) и запекает её в образ — холодный старт быстрый,
повторное скачивание не требуется. Образ включает CPU-версию torch.

Проверка:

```bash
curl http://localhost:5001/health
curl -X POST http://localhost:5001/speak \
     -H "Content-Type: application/json" \
     -d '{"text": "Привет, мир!", "voice": "xenia"}' \
     --output out.wav
```

## Подключение SUB/WAVE

`Admin → Settings → Voices → Default engine → Remote`, в поле **Server URL** указать:

```
http://host.docker.internal:5001
```

(`127.0.0.1` использовать нельзя — это loopback контейнера контроллера.) Либо LAN-IP
машины, на которой крутится TTS: `http://192.168.x.x:5001`.

Голос в `voice` пробрасывается как есть: если он совпадает с одним из голосов Silero —
используется он; иначе берётся `TTS_DEFAULT_VOICE`, а в ответ добавляются заголовки
`X-TTS-Fell-Back`, `X-TTS-Voice-Used`, `X-TTS-Fell-Back-Reason`.

## Настройки (env)

| Переменная | По умолчанию | Описание |
|---|---|---|
| `TTS_PORT` | `5001` | Порт на хосте |
| `TTS_DEFAULT_VOICE` | `xenia` | Fallback-голос |
| `TTS_SAMPLE_RATE` | `48000` | Sample rate WAV |
| `TTS_NUM_THREADS` | `0` | Потоков CPU (0 = все) |
