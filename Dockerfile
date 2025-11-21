FROM python:3.11-slim

WORKDIR /app

COPY app/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app

ENV LLM_API_BASE=http://litellm:9000
ENV LLM_MODEL_NAME=local-llama

RUN mkdir -p /app/data/audio

EXPOSE 5000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]