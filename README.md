# AI Engineering Knowledge Assistant

## Project Overview

This project aims to build a production-style AI Engineering Knowledge Assistant. It will allow users to ask engineering questions and receive answers grounded in various data sources, including system documentation, Git repositories, API documentation, runbooks, incident reports, user-uploaded documents, and web content.

## Phase 1: Project Foundation

This phase establishes the foundational elements of the project, including:

*   **Python 3.12**: The primary programming language.
*   **FastAPI**: A modern, fast (high-performance) web framework for building APIs.
*   **PostgreSQL**: A powerful, open-source relational database.
*   **Docker Compose**: For defining and running multi-container Docker applications locally.
*   **Poetry**: For dependency management.
*   **Alembic**: For managing database migrations.
*   **Basic API Endpoints**: `/health` and `/ready` for service status checks.
*   **Structured Logging**: For better observability.
*   **Configuration Management**: Using environment variables.

## Getting Started

### Prerequisites

*   Docker
*   Docker Compose
*   Poetry (optional, but recommended for local development outside Docker)

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
    docker-compose up --build -d
    ```

    This will start the FastAPI application and the PostgreSQL database.

4.  **Initialize Alembic (first time only)**:

    ```bash
    make init-db
    ```

    This command will initialize Alembic and apply any existing migrations.

### Accessing the Application

*   **FastAPI**: Accessible at `http://localhost:8000`
*   **Health Check**: `http://localhost:8000/v1/health`
*   **Readiness Check**: `http://localhost:8000/v1/ready`

### Database Migrations

*   **Create a new migration**: `make create-migration MESSAGE="Your migration message"`
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
│   │       └── health.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── db/
│   │   └── session.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── utils/
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
├── pyproject.toml
├── README.md
└── Makefile
```

## Next Steps

Refer to `docs/PROJECT_PLAN.md` for the next development phase.
