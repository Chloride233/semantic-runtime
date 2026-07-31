FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN pip install --no-cache-dir .

EXPOSE 8000

ENTRYPOINT ["python", "-m", "semantic_runtime.mcp"]
CMD []
