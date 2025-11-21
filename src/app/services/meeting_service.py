from fastapi import UploadFile
from pathlib import Path
import os

from ..audio.assembler import save_uploaded_audio
from ..audio.transcriber import transcribe_meeting_audio
from ..models.meeting import MeetingData
from .minutes_service import create_minutes_from_meeting

# Carpeta donde se guardan los audios
PROJECT_ROOT = Path(__file__).resolve().parents[3]
AUDIO_BASE_DIR = PROJECT_ROOT / "data" / "audio"
os.makedirs(AUDIO_BASE_DIR, exist_ok=True)


def normalize_participants(participants_str: str) -> list[str]:
    """
    Toma una cadena tipo: "Daniel Ariza, Equipo OT,  , Avancemétrica"
    y devuelve una lista limpia, sin duplicados ni valores vacíos.
    """
    if not participants_str:
        return ["No especificados"]

    raw = participants_str.split(",")

    cleaned: list[str] = []
    for p in raw:
        name = p.strip()
        if not name:
            continue

        # Capitalización básica: "dANIEL aRIZA" -> "Daniel Ariza"
        name = " ".join([w.capitalize() for w in name.split()])
        cleaned.append(name)

    final_list: list[str] = []
    for name in cleaned:
        if name not in final_list:
            final_list.append(name)

    return final_list or ["No especificados"]


async def process_audio_and_generate_minutes(
    file: UploadFile,
    title: str,
    participants_str: str,
) -> str:
    """
    Orquesta todo el flujo:
    - Guarda el audio
    - Transcribe el audio a MeetingData
    - Sobrescribe título y asistentes con lo enviado desde el frontend
    - Genera el acta llamando al LLM
    """
    audio_path: Path = save_uploaded_audio(file, str(AUDIO_BASE_DIR))

    # 1) Transcripción (Whisper)
    meeting: MeetingData = transcribe_meeting_audio(audio_path)

    # 2) Sobrescribir título si viene del frontend
    if title:
        meeting.title = title

    # 3) Normalizar asistentes
    participants = normalize_participants(participants_str)
    meeting.participants = participants

    # 4) Generar acta con el LLM
    minutes = await create_minutes_from_meeting(meeting)
    return minutes