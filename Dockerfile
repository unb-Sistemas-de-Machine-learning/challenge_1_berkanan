# Base image com Python 3.13, alinhada ao README e ao ambiente de produção.
FROM python:3.13-slim

# Bloco 1: dependências do sistema necessárias para bibliotecas nativas
# (scikit-learn, psycopg2, compilação de pacotes Python).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Bloco 2: definição do diretório de trabalho do app.
WORKDIR /app

# Bloco 3: cópia de dependências antes do código para cache eficiente do Docker.
COPY requirements.txt requirements.txt
COPY requirements-api.txt requirements-api.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-api.txt

# Bloco 4: cópia do código-fonte da aplicação.
COPY . .

# Exposição da porta padrão da API.
EXPOSE 8000

# Comando de início da API em produção.
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
