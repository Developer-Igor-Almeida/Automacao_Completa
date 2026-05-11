FROM python:3.11-slim

# Dependências mínimas do sistema
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    --no-install-recommends \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instala browsers do Playwright automaticamente
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]