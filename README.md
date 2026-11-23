# CloudGuardian

CloudGuardian is an infrastructure monitoring system that collects server metrics, detects anomalies, manages registered hosts, and displays infrastructure health through a web dashboard.

It includes a FastAPI backend, PostgreSQL persistence, JWT authentication, role-based access control, and a Python monitoring agent with persistent offline metric buffering.

## Features

- **System Monitoring:** Collect CPU, memory, disk, and network metrics using a Python agent.
- **Metric Ingestion:** REST APIs for storing and retrieving host metrics.
- **Anomaly Detection:** Threshold-based and statistical anomaly detection.
- **Host Management:** Register, inspect, update, and deactivate monitored hosts.
- **Authentication:** JWT-based authentication with ADMIN, OPERATOR, and VIEWER roles.
- **Dashboard:** Authenticated dashboard with host health, recent anomalies, and automatic refresh.
- **Offline Buffering:** SQLite-backed metric queue that retains pending metrics during backend outages and delivers them after recovery.
- **Database:** PostgreSQL with SQLAlchemy and Alembic migrations.
- **Testing:** Automated backend and monitoring-agent tests.

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic
- **Database:** PostgreSQL, SQLite
- **Authentication:** JWT, Argon2
- **Monitoring:** psutil, HTTPX
- **Frontend:** HTML, CSS, JavaScript
- **Migrations:** Alembic
- **Testing:** Pytest, HTTPX

## Run Locally

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
```

Configure the required environment variables in `.env`, including the PostgreSQL `DATABASE_URL` and JWT settings.

Apply database migrations:

```powershell
& ".\.venv\Scripts\python.exe" -m alembic upgrade head
```

Start the backend:

```powershell
& ".\.venv\Scripts\python.exe" -m uvicorn backend.app.main:app --reload
```

Open:

- Dashboard: http://127.0.0.1:8000/dashboard/
- API Documentation: http://127.0.0.1:8000/docs
- Health Check: http://127.0.0.1:8000/health

## Run the Monitoring Agent

Configure the following agent variables in `.env`:

```env
CLOUDGUARDIAN_API_URL=http://127.0.0.1:8000
CLOUDGUARDIAN_HOST_ID=YOUR_REGISTERED_HOST_ID
AGENT_INTERVAL_SECONDS=10
CLOUDGUARDIAN_AGENT_EMAIL=YOUR_AGENT_EMAIL
CLOUDGUARDIAN_AGENT_PASSWORD=YOUR_AGENT_PASSWORD
```

Register the host through the host management API before starting the agent.

Run:

```powershell
& ".\.venv\Scripts\python.exe" -m agent.main
```

The agent collects system metrics periodically, stores them in a local SQLite queue, and sends pending metrics to the backend. If the backend is unavailable, metrics remain queued and are retried when connectivity is restored.

## API Endpoints

| Method | Endpoint                    | Description           |
| ------ | --------------------------- | --------------------- |
| POST   | `/api/v1/auth/register`     | Register a user       |
| POST   | `/api/v1/auth/login`        | Authenticate a user   |
| POST   | `/api/v1/hosts`             | Register a host       |
| GET    | `/api/v1/hosts`             | List registered hosts |
| GET    | `/api/v1/hosts/{host_id}`   | Get host details      |
| PATCH  | `/api/v1/hosts/{host_id}`   | Update host           |
| DELETE | `/api/v1/hosts/{host_id}`   | Deactivate host       |
| POST   | `/api/v1/metrics`           | Ingest metrics        |
| GET    | `/api/v1/metrics`           | Retrieve metrics      |
| GET    | `/api/v1/metrics/hosts`     | Get host health       |
| GET    | `/api/v1/metrics/anomalies` | Retrieve anomalies    |

Protected endpoints require a valid JWT access token. Access permissions depend on the assigned role.

## Run Tests

Run the complete test suite:

```powershell
& ".\.venv\Scripts\python.exe" -m pytest -q
```

## Project Structure

```text
CloudGuardian/
├── agent/
│   ├── collectors/
│   ├── core/
│   └── storage/
├── backend/
│   └── app/
│       ├── api/
│       ├── core/
│       ├── models/
│       ├── schemas/
│       ├── services/
│       └── main.py
├── frontend/
│   └── index.html
├── tests/
├── alembic/
├── requirements.txt
└── README.md
```

## Security Notes

- Keep `.env`, database files, passwords, and JWT secrets out of version control.
- Use strong, unique secrets for JWT signing.
- Assign users only the permissions they require.
- Keep agent credentials private.
