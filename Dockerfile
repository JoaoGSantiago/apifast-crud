FROM python:3.14-slim AS builder

WORKDIR /tmp

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
