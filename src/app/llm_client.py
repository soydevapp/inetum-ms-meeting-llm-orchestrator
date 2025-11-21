import os
import httpx
from .models.meeting import MeetingData, MeetingSegment  # asegúrate de importar MeetingSegment si lo usas

LITELLM_BASE_URL = os.getenv("LLM_API_BASE", "http://localhost:9000")
LLM_MODEL = os.getenv("LLM_MODEL_NAME", "local-llama")
LLM_MOCK = os.getenv("LLM_MOCK", "false").lower() == "true"


def _generate_mock_minutes(meeting: MeetingData) -> str:
    """
    Genera un acta de ejemplo sin llamar a ningún LLM.
    Útil para desarrollo cuando LiteLLM/Ollama no están disponibles.
    """
    transcript_preview = "\n".join(
        f"- {s.speaker}: {s.text[:80]}{'...' if len(s.text) > 80 else ''}"
        for s in meeting.segments[:5]
    )

    participants = ", ".join(meeting.participants)

    return f"""# Acta de reunión (MOCK)

- Título: {meeting.title}
- Fecha: {meeting.date}
- Asistentes: {participants}

## Resumen ejecutivo

Este es un acta generada en modo **mock**. No se ha llamado a ningún modelo LLM.
Se ha recibido una transcripción con {len(meeting.segments)} intervenciones.

## Puntos tratados (derivados de la transcripción)

{transcript_preview}

## Decisiones

1. [MOCK] Validar integración con LiteLLM en entorno local.
2. [MOCK] Sustituir este mock por llamadas reales a Ollama/vLLM cuando estén disponibles.

## Acciones

| Acción                                        | Responsable | Fecha objetivo |
|-----------------------------------------------|-------------|----------------|
| Probar el endpoint /minutes en modo mock      | {meeting.participants[0] if meeting.participants else 'N/A'} | Pendiente       |
| Levantar LiteLLM y probar modo real           | N/A         | Pendiente       |
"""


async def generate_minutes_with_llm(meeting: MeetingData) -> str:
    """
    Si LLM_MOCK=true -> devuelve un acta mock.
    Si no -> llama a LiteLLM (Ollama / vLLM / lo que esté detrás).
    """
    if LLM_MOCK:
        return _generate_mock_minutes(meeting)

    transcript_for_prompt = "\n".join(
        f"[{s.start:.1f}-{s.end:.1f}] {s.speaker}: {s.text}"
        for s in meeting.segments
    )

    system_prompt = """
Eres un generador experto de actas de reunión corporativas para un departamento de Arquitectura y Oficina Técnica.

Tu salida debe ser SIEMPRE un documento en **Markdown profesional**, siguiendo EXACTAMENTE esta estructura:

# <Título de la reunión>
- **Fecha:** <fecha ISO o formato DD/MM/YYYY>
- **Asistentes:**
  * Nombre 1
  * Nombre 2
  * ...

---

## 1. Resumen ejecutivo
Explica en 3–6 líneas los objetivos de la reunión, el contexto y los resultados clave.
Debe ser claro, conciso y formal.

## 2. Puntos tratados
Lista numerada con los temas tratados.
Cada punto debe estar redactado de forma profesional, sin divagar, sin repeticiones y correctamente categorizado.

Ejemplo:
1. Seguimiento de actividades planificadas.
2. Revisión de riesgos e impedimentos.
3. Análisis del estado de los proyectos activos.
4. Alineación de prioridades para el sprint o la semana.

## 3. Decisiones tomadas
Registra únicamente las decisiones realmente tomadas.
Si no se toma ninguna, indica:
- *No se registraron decisiones en esta sesión.*

## 4. Acciones y Seguimiento
Devuelve SIEMPRE una tabla en Markdown con las siguientes columnas:

| Acción | Responsable | Prioridad | Fecha objetivo | Estado |
|--------|-------------|-----------|----------------|--------|
| Descripción clara | Persona | Alta/Media/Baja | YYYY-MM-DD | Pendiente |

Reglas:
- Las acciones deben derivarse del contenido de la transcripción.
- Los responsables DEBEN pertenecer a la lista de asistentes.
- La fecha objetivo puede estimarse si no está explícita.
- El estado por defecto es **Pendiente**.

---

### Reglas de estilo
- Debe sonar corporativo, formal y orientado a seguimiento.
- Nada de frases vagas o genéricas.
- No inventes datos ajenos a la transcripción.
- No rumores, no opiniones, no información fuera del contexto.
- Mantén la puntuación correcta.
- No uses emojis.
- No incluyas texto adicional fuera de la estructura.
"""

    user_prompt = f"""
Datos de la reunión:
Título: {meeting.title}
Fecha: {meeting.date}
Participantes: {", ".join(meeting.participants)}

Transcripción:
{transcript_for_prompt}
"""

    body = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{LITELLM_BASE_URL}/chat/completions",
            json=body,
            timeout=60.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]