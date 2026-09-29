FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home appuser
COPY serp serp
COPY data data
RUN mkdir /app/output && chown appuser /app/output
USER appuser
CMD ["python", "-m", "serp.cli"]
