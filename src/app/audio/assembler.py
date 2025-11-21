import os
import uuid
from pathlib import Path
from fastapi import UploadFile


def save_uploaded_audio(file: UploadFile, base_dir: str) -> Path:
    """
    Guarda el fichero de audio subido en disco y devuelve la ruta.
    En el futuro aquí puedes añadir lógica de normalización de formato (ffmpeg, etc.).
    """
    os.makedirs(base_dir, exist_ok=True)

    extension = os.path.splitext(file.filename)[1] or ".webm"
    meeting_id = str(uuid.uuid4())
    filename = f"{meeting_id}{extension}"
    filepath = Path(base_dir) / filename

    # Guardamos el binario
    with open(filepath, "wb") as f:
        # importante leer el contenido asíncrono correctamente desde FastAPI
        content = file.file.read()
        f.write(content)

    return filepath