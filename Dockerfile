#build stage
FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY . .

#run stage (settings and start command)
ENV PYTHONPATH=/app/src
ENV BOOKS_DB=/data/books.db
VOLUME /data

EXPOSE 5000

CMD ["uv", "run", "--no-sync", "python", "src/tp_1/app.py"]
