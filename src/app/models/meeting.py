from pydantic import BaseModel
from typing import List


class MeetingSegment(BaseModel):
    speaker: str
    start: float
    end: float
    text: str


class MeetingData(BaseModel):
    """
    Representa la transcripción estructurada de una reunión.
    Esto es lo que debe producir tu pipeline de STT + diarización (WhisperX en el futuro).
    """
    title: str
    date: str
    participants: List[str]
    segments: List[MeetingSegment]