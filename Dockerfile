FROM python:3.12-slim as builder

ENV PYTHONUNBUFFERED=1 \
    POETRY_HOME="/usr/local" \
    POETRY_VERSION="1.8.1"

RUN apt-get update \
    && apt-get install --no-install-recommends -y curl \
    && curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

FROM python:3.12-slim as runner

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

ENTRYPOINT ["gunicorn", "rinha.wsgi", "-b", "0:8080"]