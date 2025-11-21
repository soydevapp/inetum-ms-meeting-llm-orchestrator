# Proyecto: inetum-ms-meeting-llm-orchestrator

inetum-ms-meeting-llm-orchestrator es un microservicio Python orientado a:
• Orquestar modelos LLM a través de LiteLLM
• Gestionar la generación de actas de reunión
• Integrarse con futuros módulos de:
• Grabación de audio
• Transcripción (WhisperX)
• Diarización
• Procesamiento de contexto

Forma parte del ecosistema Inetum Meeting Assistant.

# Arquitectura funcional

```plaintext
[inetum-mfe-meeting-recorder]  (frontend)
           |
           v
[inetum-ms-meeting-llm-orchestrator]  (backend)
  1) Recibe audio (binario)
  2) Lo guarda / transforma (ffmpeg, etc.)
  3) Llama a WhisperX (STT + diarización)
  4) Genera MeetingData (JSON estructurado)
  5) Llama a LiteLLM con MeetingData → prompt
           |
           v
       [LiteLLM]
           |
           v
   [Ollama / vLLM / lo que definas]
           |
           v
  6) Devuelve acta al orquestador
  7) El orquestador devuelve acta al frontend
```

El microservicio se encarga de:
• Unificar los datos de reunión
• Construir prompts estructurados
• Generar actas profesionales
• Gestionar interacciones con LLM locales

# Requisitos

    •	Python 3.11+
    •	Docker / Docker Compose
    •	LiteLLM ejecutándose en http://localhost:9000
    •	Ollama (PoC) o vLLM (producción futura)

# Ejecución local (Docker)

```bash
docker compose -f docker-compose.local.yml up --build
```

Servicios expuestos:
• API FastAPI → http://localhost:5000
• Docs OpenAPI → http://localhost:5000/docs

# Probar generación de audio

```bash
POST http://localhost:5000/minutes
Content-Type: application/json
```

Payload

```json
{
  "title": "Reunión Comité Arquitectura",
  "date": "2025-01-01T10:00:00Z",
  "participants": ["Daniel", "María", "Javier"],
  "segments": [
    {
      "speaker": "Daniel",
      "start": 0,
      "end": 10,
      "text": "Buenos días, revisamos el estado de los canales digitales."
    }
  ]
}
```

# Estructura de proyecto

    •	src/app/main.py: arranque de FastAPI
    •	src/app/llm_client.py: integración LiteLLM
    •	src/app/models: modelos Pydantic
    •	src/app/services: lógica de negocio
    •	src/app/audio: futuro pipeline de audio/WhisperX

# LLMs Soportados

    •	Ollama (PoC)
    •	vLLM (producción)
    •	OpenAI / Azure / Anthropic / etc. (si se habilita, no por defecto)

# Roadmap

**Fase PoC**

    •	Generación básica de actas vía LLM
    •	Integración WhisperX en contenedor
    •	Soporte para cargar audio chunked

**Fase Coportativa**

    •	Despliegue con vLLM en servidor dedicado
    •	Observabilidad (OTEL)
    •	Auditoría de llamadas al LLM
    •	Input multimodal (audio + transcripción + metadatos)

# Arranque del proyecto

- Es necestario tener levantado LiteLLM en http://localhost:8000
- Es necesario tener levantado el filtro en http://localhost:9000

```bash
PYTHONPATH=src uvicorn app.main:app --reload --host 0.0.0.0 --port 9002
```

# Cada vez que instalamos o quitamos dependencias

```bash
pip freeze > requirements.txt
```
