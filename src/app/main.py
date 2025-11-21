from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware

from .models.meeting import MeetingData
from .models.minutes import MinutesResponse
from .services.minutes_service import create_minutes_from_meeting
from .services.meeting_service import process_audio_and_generate_minutes


app = FastAPI(
    title="inetum-ms-meeting-llm-orchestrator",
    version="0.1.0",
    description="Microservicio para orquestar la generación de actas de reunión vía LLM",
)

# Ajusta los orígenes según tu frontend real
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/minutes", response_model=MinutesResponse)
async def create_minutes(meeting: MeetingData):
    try:
        minutes = await create_minutes_from_meeting(meeting)
        return MinutesResponse(minutes=minutes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/meetings/upload-audio", response_model=MinutesResponse)
async def upload_audio_and_get_minutes(
    file: UploadFile = File(...),
    title: str = Form("Reunión sin título"),
    participants: str = Form("Speaker_1"),
):
    try:
        minutes = await process_audio_and_generate_minutes(
            file=file,
            title=title,
            participants_str=participants,
        )
        return MinutesResponse(minutes=minutes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))