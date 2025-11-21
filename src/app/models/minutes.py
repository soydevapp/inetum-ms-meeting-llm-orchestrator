from pydantic import BaseModel


class MinutesResponse(BaseModel):
    """
    Respuesta básica del microservicio con el acta generada.
    """
    minutes: str