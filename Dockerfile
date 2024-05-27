FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

# TODO: fix to poetry style
WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . .

# TODO: fix to project structure
# CMD ["poetry", "run", "sync_files"]
CMD ["poetry", "run", "python", "-m", "drive_inventory.entrypoints.sync_files"]
