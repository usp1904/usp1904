FROM python:3.11-slim

WORKDIR /app

# System deps for sqlite + build
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything (enterprise, services, agents, templates, etc.)
COPY . /app/

# Fly expects 8080, but respect $PORT
ENV PORT=8080
ENV UVICORN_WORKERS=2
ENV DATABASE_URL=sqlite:///cbse_content.db
ENV ALLOWED_HOSTS=*
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["/bin/sh", "start.sh"]
