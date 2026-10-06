````markdown
# Tailored Tech Task

FastAPI microservice with persistent caching for transformed payloads.

## Requirements

- Python 3.12+
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic Settings
- HTTPX

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
````

## Run

### Local

```bash
uvicorn app.main:app --reload
```

API: `http://localhost:8000`

Swagger: `http://localhost:8000/docs`

### Docker

```bash
docker compose up --build
```

## API

### Create Payload

```http
POST /payload
```

```json
{
  "list_1": ["hello", "world"],
  "list_2": ["foo", "bar"]
}
```

Response:

```json
{
  "id": "..."
}
```

The lists must have the same length.

### Get Payload

```http
GET /payload/{id}
```

Response:

```json
{
  "output": "HELLO, FOO, WORLD, BAR"
}
```

## Caching

Two persistent caches are used:

* **Transformation cache:** stores the transformed result for each individual input string.
* **Payload cache:** stores the generated output using a deterministic SHA-256 hash of `[list_1, list_2]` as the payload ID.

The same input lists therefore return the same payload ID without repeating transformations.

## CLI

The CLI communicates with the running API.

```bash
python -m app.cli \
  -j '{"list_1":["hello","world"],"list_2":["foo","bar"]}'
```

Options:

| Option           | Description                 |
| ---------------- | --------------------------- |
| `--host`         | Cache server URL            |
| `-r`, `--repeat` | Number of requests          |
| `-i`, `--input`  | Input file; `-` for stdin   |
| `-j`, `--json`   | Input JSON                  |
| `-o`, `--output` | Output file; `-` for stdout |
| `-h`, `--help`   | Show help                   |

The task specification uses `-h` for both `--host` and `--help`. The implementation uses `-h` for help and reports a hint to use `--host` when `-h` is followed by a host value.

## Testing

```bash
python -m pytest -v
```

Tests cover the API, validation, payload ID generation, transformation caching, and CLI arguments.

## Project Structure

```text
app/
├── cli.py
├── dao.py
├── database.py
├── main.py
├── models.py
├── service.py
├── tables.py
└── transformer.py

tests/
├── test_api.py
├── test_cli.py
└── test_service.py

Dockerfile
compose.yaml
requirements.txt
README.md
```

```
```
