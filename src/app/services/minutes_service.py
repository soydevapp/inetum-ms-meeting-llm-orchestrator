from ..models.meeting import MeetingData
from ..llm_client import generate_minutes_with_llm


async def create_minutes_from_meeting(meeting: MeetingData) -> str:
    """
    Lógica de negocio para generar un acta a partir de una MeetingData.
    Ahora mismo solo delega en el cliente LLM, pero aquí podrías:
    - Enriquecer datos
    - Aplicar reglas de negocio
    - Guardar histórico, etc.
    """
    minutes = await generate_minutes_with_llm(meeting)
    return minutes