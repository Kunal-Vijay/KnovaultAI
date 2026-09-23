# AI Engineering Knowledge Assistant

## Project Overview

This project aims to build a production-style AI Engineering Knowledge Assistant. It will allow users to ask engineering questions and receive answers grounded in various data sources, including system documentation, Git repositories, API documentation, runbooks, incident reports, user-uploaded documents, and web content.

## Phase 1: Project Foundation

This phase establishes the foundational elements of the project, including:

*   **Python 3.12**: The primary programming language.
*   **FastAPI**: A modern, fast (high-performance) web framework for building APIs.
*   **PostgreSQL**: A powerful, open-source relational database.
*   **Docker Compose**: For defining and running multi-container Docker applications locally.
*   **pip and requirements.txt**: For dependency management.
*   **Alembic**: For managing database migrations.
*   **Basic API Endpoints**: `/health` and `/ready` for service status checks.
*   **Structured Logging**: For better observability.
*   **Configuration Management**: Using environment variables.

## Getting Started

### Prerequisites

*   Docker
*   Docker Compose
*   Python 3.12 (optional, if running locally outside Docker)

### Setup

1.  **Clone the repository**:

    ```bash
    git clone <repository-url>
    cd ai-engineering-assistant
    ```

2.  **Create `.env` file**:

    Copy the `.env.example` to `.env` and configure your environment variables, especially `DATABASE_URL` if you're not using the default Docker Compose values.

    ```bash
    cp .env.example .env
    ```

3.  **Build and run services with Docker Compose**:

    ```bash
    docker compose up --build -d
    ```

    This will start the FastAPI application and the PostgreSQL database.

4.  **Initialize Alembic (first time only)**:

    ```bash
    docker compose exec fastapi_app sh -c "alembic init -t async migrations"
    ```

    This command will initialize Alembic and create the `migrations` directory and `alembic.ini` file if they don't exist. *If it says "Directory migrations already exists and is not empty", you can skip this step and proceed.* 

5.  **Create the initial migration for Phase 2 & 3 models**:

    ```bash
    docker compose exec fastapi_app sh -c "alembic revision --autogenerate -m \"Create user, knowledge base, document, document chunk tables and ingestion fields\""
    ```

6.  **Apply the migrations**: 

    ```bash
    docker compose exec fastapi_app alembic upgrade head
    ```

### Accessing the Application

*   **FastAPI**: Accessible at `http://localhost:8000`
*   **Health Check**: `http://localhost:8000/v1/health`
*   **Readiness Check**: `http://localhost:8000/v1/ready`

### Database Migrations

*   **Create a new migration**: `MESSAGE="Your migration message" make create-migration`
*   **Apply migrations**: `make migrate-db`

### Testing

*   Run tests: `make test`

### Linting and Formatting

*   Lint code: `make lint`
*   Format code: `make format`

## Project Structure

```
ai-engineering-assistant/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── v1/
│   │       ├── documents.py
│   │       ├── health.py
│   │       ├── knowledge_bases.py
│   │       └── users.py
│   ├── core/
│   │   ├── config.py
│   │   ├── embedding.py
│   │   ├── logging.py
│   │   └── storage.py
│   ├── db/
│   │   └── session.py
│   ├── ingestion/
│   │   ├── chunkers/
│   │   │   └── __init__.py
│   │   ├── metadata_extractors/
│   │   │   └── __init__.py
│   │   └── parsers/
│   │       └── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── document.py
│   │   ├── document_chunk.py
│   │   ├── knowledge_base.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── document.py
│   │   ├── document_chunk.py
│   │   ├── knowledge_base.py
│   │   └── user.py
│   └── services/
│       ├── document.py
│       ├── ingestion.py
│       ├── knowledge_base.py
│       └── user.py
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── migrations/
├── scripts/
│   └── init_alembic.sh
├── docker/
│   ├── Dockerfile.fastapi
│   └── Dockerfile.postgres
├── .env.example
├── docker-compose.yml
├── requirements.txt
├── README.md
└── Makefile
```

## Next Steps

Refer to `docs/PROJECT_PLAN.md` for the next development phase.
