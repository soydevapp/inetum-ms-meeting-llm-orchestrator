from datetime import datetime
from pathlib import Path
from typing import List
import os

from ..models.meeting import MeetingData, MeetingSegment

import torch
import whisper


def _get_device() -> str:
    """
    De momento forzamos CPU porque en tu entorno MPS (Metal) con Torch
    ha dado problemas con algunas operaciones. En un M4 la CPU va sobrada
    para esta PoC.
    """
    return "cpu"


def transcribe_meeting_audio(audio_path: Path, language: str = "es") -> MeetingData:
    """
    Transcribe el audio usando Whisper (openai-whisper).
    No hace diarización por ahora: todos los segmentos serán 'Speaker_1'.

    - Usa CPU (más estable en tu entorno actual).
    - Devuelve un MeetingData con segmentos y timestamps.
    """

    device = _get_device()
    print(f"[whisper] Usando dispositivo: {device}")

    # Puedes ajustar el modelo: "tiny", "base", "small", "medium", "large"
    model_name = os.getenv("WHISPER_MODEL", "small")
    print(f"[whisper] Cargando modelo: {model_name}")
    model = whisper.load_model(model_name, device=device)

    print(f"[whisper] Transcribiendo audio: {audio_path}")
    result = model.transcribe(str(audio_path), language=language)

    segments_raw = result.get("segments", [])
    print(f"[whisper] Segmentos obtenidos: {len(segments_raw)}")

    meeting_segments: List[MeetingSegment] = []

    for seg in segments_raw:
        start = float(seg.get("start", 0.0))
        end = float(seg.get("end", 0.0))
        text = seg.get("text", "").strip()
        if not text:
            continue

        meeting_segments.append(
            MeetingSegment(
                speaker="Speaker_1",  # sin diarización de momento
                start=start,
                end=end,
                text=text,
            )
        )

    if not meeting_segments:
        meeting_segments.append(
            MeetingSegment(
                speaker="Speaker_1",
                start=0.0,
                end=0.0,
                text="(No se ha podido transcribir contenido del audio.)",
            )
        )

    title = f"Reunión transcrita - {audio_path.name}"
    date = datetime.utcnow().isoformat() + "Z"
    participants: List[str] = []  # se rellena en meeting_service

    return MeetingData(
        title=title,
        date=date,
        participants=participants,
        segments=meeting_segments,
    )