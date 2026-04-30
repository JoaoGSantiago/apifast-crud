FROM python:3.13-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

COPY . .

FROM gcr.io/distroless/python3-debian13:nonroot

ENV PYTHONUNBUFFERED=1 \
	PYTHONPATH=/install/lib/python3.13/site-packages \
	PATH=/install/bin:$PATH

WORKDIR /app

COPY --from=builder /install /install
COPY --from=builder /app /app

EXPOSE 8000

CMD ["-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
