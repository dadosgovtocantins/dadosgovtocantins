# Imagem base dos Cloud Run Jobs de ingestão.
# Sem Playwright de propósito: o browser só é necessário para scraping complexo
# (task 18, condicional ao Gate 1) e pesaria ~400 MB no boot de TODO coletor
# federal, consumindo vCPU-s da franquia gratuita sem contrapartida.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependências de sistema do PySUS (leitura DBC/DBF do DATASUS)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala SEMPRE do lock — reprodutibilidade e defesa contra dependency
# confusion: índice oficial explícito, nenhuma fonte extra (S14, S20).
COPY requirements.lock.txt .
RUN pip install --no-cache-dir --index-url https://pypi.org/simple \
        -r requirements.lock.txt \
    && apt-get purge -y build-essential && apt-get autoremove -y

COPY pyproject.toml ./
COPY src/ ./src/
COPY tests/ ./tests/
COPY README.md LICENSE ./

# Testes rodam no build: imagem que não passa nos testes não existe.
RUN pip install --no-cache-dir pytest && pytest -q && pip uninstall -y pytest

# Roda como usuário sem privilégio (S12 — menor privilégio)
RUN useradd --create-home --uid 1000 coletor && chown -R coletor:coletor /app
USER coletor

ENTRYPOINT ["python", "-m", "src.cli"]
CMD ["--help"]
