# Faster API

## Description
`Ongoing`

## Stack
**App**:  [Python](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/),
[Docker](https://www.docker.com/), [Postgres](https://www.postgresql.org/),
[SQLAlchemy](https://www.sqlalchemy.org/), [Pydantic](https://docs.pydantic.dev/latest/),
[Alembic](https://alembic.sqlalchemy.org/en/latest/), [Uvicorn](https://uvicorn.dev/),
[Gunicorn](https://gunicorn.org/), [Pybabel (i18n)](https://babel.pocoo.org/en/latest/cmdline.html)

**Tests**: [Pytest](https://docs.pytest.org/en/stable/)

**Code formating**: [ruff](https://docs.astral.sh/ruff/), [pyupgrade](https://github.com/asottile/pyupgrade), [pre-commit](https://pre-commit.com/)

**Python environment & dependency manager**: [uv](https://docs.astral.sh/uv/)

**Observability**: [OpenTelemetry](https://opentelemetry.io/), [Grafana](https://grafana.com/), [Prometheus](https://prometheus.io/), [Grafana Tempo](https://grafana.com/docs/tempo/latest/)


## How to run
Clone the repository, then open it:
```bash
git clone https://github.com/gusttavofelipe/faster-api.git
```

Copy and fill credentials from `.example.env` to `.env`:
```bash
make env
```

Bring the database up:
```bash
make up
```

Set up the project:
```bash
make setup
```


Run the API:
```bash
make run
```

Acess http://localhost:8001/docs to see the endpoints
