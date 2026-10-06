# Tailored Tech Task

FastAPI microservice implementing a persistent caching layer for transformed payloads.

## Requirements

* Python 3.12+
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic / Pydantic Settings
* HTTPX
* Docker

## Project Structure

```text
.
├── app/
│   ├── cli.py
│   ├── dao.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── service.py
│   ├── tables.py
│   └── transformer.py
├── tests/
│   ├── test_api.py
│   ├── test_cli.py
│   └── test_service.py
├── Dockerfile
├── compose.yaml
├── requirements.txt
└── README.md
```

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run Locally

Start the API:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

## Docker

Build and start the service:

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

SQLite data is stored in a Docker volume so the cache persists when the container is recreated.

## API

### Create Payload

```http
POST /payload
Content-Type: application/json
```

Request:

```json
{
  "list_1": ["hello", "world", "python"],
  "list_2": ["foo", "bar", "fastapi"]
}
```

Response:

```json
{
  "id": "..."
}
```

The two lists must have the same length.

### Get Payload

```http
GET /payload/{id}
```

Response:

```json
{
  "output": "HELLO, FOO, WORLD, BAR, PYTHON, FASTAPI"
}
```

A nonexistent payload ID returns `404`.

## Caching

The service uses two persistent caches.

### Transformation Cache

Each individual input string is cached:

```text
input -> transformed output
```

If the same string appears in subsequent requests, the transformer is not called again.

### Payload Cache

The complete pair of input lists is converted into a deterministic SHA-256 hash.

The hash is calculated from:

```text
[list_1, list_2]
```

List order is preserved because it affects the resulting interleaved payload.

The resulting hash is used as the payload ID:

```text
input lists -> SHA-256 hash -> payload ID
```

Therefore, submitting exactly the same two lists returns the same payload ID without recreating the payload.

## CLI

The CLI communicates with the running API over HTTP.

### JSON Input

```bash
python -m app.cli \
  -j '{"list_1":["hello","world"],"list_2":["foo","bar"]}'
```

### Repeat Requests

```bash
python -m app.cli \
  -j '{"list_1":["hello","world"],"list_2":["foo","bar"]}' \
  -r 3
```

### Input File

```bash
python -m app.cli -i input.json
```

### Standard Input

```bash
cat input.json | python -m app.cli -i -
```

### Output File

```bash
python -m app.cli \
  -j '{"list_1":["hello"],"list_2":["world"]}' \
  -o result.json
```

### Custom Server

```bash
python -m app.cli \
  --host http://localhost:8000 \
  -j '{"list_1":["hello"],"list_2":["world"]}'
```

### CLI Options

| Option           | Description                   |
| ---------------- | ----------------------------- |
| `--host`         | URL of the cache server       |
| `-r`, `--repeat` | Number of requests to send    |
| `-i`, `--input`  | Input file; `-` means stdin   |
| `-j`, `--json`   | Input JSON                    |
| `-o`, `--output` | Output file; `-` means stdout |
| `-h`, `--help`   | Show help                     |

The task specification contains a conflict between `-h` for `--host` and `-h` for `--help`. The implementation treats `-h` as the conventional help option. When `-h` is followed by a host value, the CLI reports:

```text
error: argument -h: did you mean '--host'?
```

## Testing

Run the complete test suite:

```bash
python -m pytest -v
```

The tests cover:

* API payload creation
* API payload retrieval
* Missing payloads
* Input validation
* Deterministic payload IDs
* Different payload IDs for different inputs
* Transformation cache reuse
* Repeated values
* CLI argument handling

## Design

The application is divided into a small number of layers:

```text
HTTP / CLI
    |
    v
API
    |
    v
Service
    |
    v
DAO
    |
    v
SQLAlchemy / SQLite
```

The service layer owns the caching and payload-generation logic.

The DAO layer handles database access.

The API models validate incoming and outgoing HTTP data.

The SQLAlchemy models represent the persistent cache tables.

The transformer is kept separate because it represents the operation whose results are being cached.

## Database

Two tables are used.

### `transformation_cache`

| Column   | Purpose                      |
| -------- | ---------------------------- |
| `input`  | Original string; primary key |
| `output` | Transformed string           |

### `payload_cache`

| Column   | Purpose                               |
| -------- | ------------------------------------- |
| `hash`   | Deterministic payload ID; primary key |
| `output` | Generated payload                     |

SQLite is used because the task requires persistent caching but does not require a separate database server.

## Assumptions

* The two input lists must have equal lengths because their elements are interleaved pair-by-pair.
* Input list order is significant.
* The SHA-256 hash of the canonical JSON representation is used as the payload identifier.
* Transformation results are deterministic for a given input.
* The cache is persistent across application restarts.
* The provided transformer is a local stand-in for the simulated external transformation operation.
