# CloudGuardian

**AI-Powered Predictive Maintenance and Anomaly Detection for Cloud and Server Infrastructure**

CloudGuardian is an infrastructure monitoring and predictive maintenance project designed to collect server metrics and logs, detect anomalies, monitor host health, and eventually predict infrastructure failures using machine learning.

It features a FastAPI backend, PostgreSQL persistence, JWT authentication, role-based access control, a Python monitoring agent with persistent offline metric buffering, and Drain3-powered log parsing and template clustering.

## Project Status

<escape>**Estimated Overall Completion: 45%**</escape>

<escape>**Current Stage:** Core Monitoring + Log Ingestion Completed | Predictive AI Development Pending</escape>

Progress is estimated against the complete research vision, including predictive modeling, multimodal learning, explainability, and production deployment.

| Development Area | Status |
|---|---|
| Backend foundation and database | Complete |
| Authentication and RBAC | Complete |
| Host management | Complete |
| Metrics ingestion and storage | Complete |
| Anomaly detection | Initial implementation complete |
| Monitoring agent | Initial implementation complete |
| Offline metric buffering | Complete |
| Log ingestion and Drain3 parsing | Initial implementation complete |
| Dashboard | Initial implementation complete |
| Predictive ML models | Pending |
| Multimodal AI fusion | Pending |
| Explainability and calibration | Pending |
| Production deployment | Pending |

## Features Implemented

- **System Monitoring:** Collect CPU, memory, disk, and network metrics using a Python monitoring agent.
- **Metric Ingestion:** REST APIs for storing and retrieving host metrics.
- **Anomaly Detection:** Threshold-based and statistical anomaly detection.
- **Host Management:** Register, inspect, update, and deactivate monitored hosts.
- **Log Processing:** Parse infrastructure logs using Drain3 and identify recurring patterns.
- **Log Template Clustering:** Group similar log messages using host-specific Drain3 clusters.
- **Secret Redaction:** Redact common credentials and bearer tokens from ingested logs.
- **Authentication:** JWT-based authentication with ADMIN, OPERATOR, and VIEWER roles.
- **Dashboard:** Authenticated dashboard displaying host health and recent anomalies.
- **Offline Buffering:** SQLite-backed metric queue with retry and recovery support.
- **Database:** PostgreSQL with SQLAlchemy and Alembic migrations.
- **Automated Testing:** Backend, monitoring-agent, parser, and API tests.

## Development Roadmap

### Phase 1 — Backend Foundation and Infrastructure

<escape>**Status: Complete (100%)**</escape>

- [x] FastAPI application setup
- [x] PostgreSQL database integration
- [x] SQLAlchemy models and database sessions
- [x] Alembic migration setup
- [x] Metrics ingestion and retrieval APIs
- [x] Threshold-based anomaly detection
- [x] Statistical anomaly detection

**Checkpoint:** A working backend capable of storing infrastructure metrics and detecting anomalies.

### Phase 2 — Authentication and Host Management

<escape>**Status: Complete (100%)**</escape>

- [x] JWT authentication
- [x] Password hashing using Argon2
- [x] User registration and login
- [x] Role-based access control
- [x] ADMIN, OPERATOR, and VIEWER roles
- [x] Host registration and management
- [x] Host status validation during metric ingestion

**Checkpoint:** Secure infrastructure APIs with role-based permissions and host lifecycle management.

### Phase 3 — Monitoring Agent and Reliability

<escape>**Status: Complete (100% of initial implementation)**</escape>

- [x] System metric collection using psutil
- [x] HTTPX-based backend communication
- [x] JWT authentication for the agent
- [x] Periodic metric collection
- [x] SQLite-backed offline metric buffering
- [x] Retry mechanism with exponential backoff
- [x] Recovery and delivery of queued metrics after backend outages

**Checkpoint:** A monitoring agent that continues collecting metrics during backend downtime and delivers pending data after recovery.

### Phase 4 — Log Processing and Template Mining

<escape>**Status: Initial Implementation Complete (85%)**</escape>

- [x] Log ingestion API
- [x] Host validation for log ingestion
- [x] Log severity validation
- [x] Sensitive credential redaction
- [x] Drain3-based log parsing
- [x] Host-specific template clustering
- [x] Persistent Drain3 parser state
- [x] PostgreSQL log event storage
- [x] PostgreSQL log template storage
- [x] Database transaction rollback handling
- [x] Drain3 persistence failure handling
- [x] Automated log parser and API tests

**Remaining checkpoints:**

- [ ] Concurrency protection for host-specific Drain3 miners
- [ ] Stronger crash-recovery and parser/database consistency
- [ ] Automated log collection from monitored hosts
- [ ] Log filtering, search, and visualization in the dashboard

**Checkpoint:** A reliable log-processing pipeline that extracts recurring patterns and stores structured log events.

### Phase 5 — Monitoring Dashboard and Visualization

<escape>**Status: Initial Implementation Complete (60%)**</escape>

- [x] Authenticated dashboard
- [x] Login and logout
- [x] Host health visualization
- [x] Recent anomaly display
- [x] Manual metric submission
- [x] Automatic dashboard refresh
- [ ] Log monitoring interface
- [ ] Historical metric charts
- [ ] Host-specific metric and log timelines
- [ ] Predictive risk visualization
- [ ] Failure prediction and alert interface

**Checkpoint:** A unified interface for infrastructure health, metrics, logs, anomalies, and predictive insights.

### Phase 6 — Predictive Machine Learning

<escape>**Status: Pending (0%)**</escape>

This phase introduces the main research contribution of CloudGuardian.

- [ ] Collect and prepare time-aligned infrastructure datasets
- [ ] Establish baseline anomaly detection models
- [ ] Implement Temporal Convolutional Network (TCN)
- [ ] Develop metric forecasting and reconstruction models
- [ ] Develop log-sequence representations using Drain3 templates
- [ ] Implement multimodal fusion using cross-attention
- [ ] Develop predictive risk estimation
- [ ] Implement time-to-failure estimation
- [ ] Evaluate model performance against baseline approaches

**Checkpoint:** A predictive model capable of learning from infrastructure metrics and logs to identify potential failures before they occur.

### Phase 7 — Explainability, Calibration, and Alert Governance

<escape>**Status: Pending (0%)**</escape>

- [ ] Implement conformal prediction for uncertainty calibration
- [ ] Develop online false discovery rate (FDR) alert control
- [ ] Implement alert hysteresis and cooldown mechanisms
- [ ] Integrate SHAP-based explanations
- [ ] Develop counterfactual analysis
- [ ] Generate root-cause evidence for predicted anomalies

**Checkpoint:** Trustworthy and explainable predictive alerts with controlled false positives.

### Phase 8 — Production Readiness and Deployment

<escape>**Status: Pending (initial groundwork only)**</escape>

- [ ] Dockerize backend and monitoring agent
- [ ] Docker Compose deployment
- [ ] Production configuration and secrets management
- [ ] Structured logging and observability
- [ ] Performance and load testing
- [ ] MLflow experiment tracking
- [ ] ONNX Runtime model inference
- [ ] Deployment and operational documentation

**Checkpoint:** A reproducible, deployable infrastructure monitoring and predictive maintenance platform.

## Upcoming Development Priorities

The next implementation milestones are:

| Priority | Task | Expected Outcome |
|---|---|---|
| P0 | Drain3 concurrency protection | Safe concurrent log processing |
| P0 | Parser crash recovery | Consistent parser and database state |
| P1 | Automated log collection | Continuous infrastructure log ingestion |
| P1 | Dashboard log interface | Searchable and filterable log events |
| P1 | Historical metric visualization | Time-series infrastructure insights |
| P2 | Dataset preparation | Aligned metric and log training data |
| P2 | TCN implementation | Metric-based predictive modeling |
| P2 | Multimodal fusion | Joint metric and log intelligence |
| P3 | Explainability and calibration | Reliable predictive alerts |
| P3 | Production deployment | End-to-end deployable system |

## Technology Stack

| Component | Technologies |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, Pydantic |
| Database | PostgreSQL, SQLite |
| Authentication | JWT, Argon2 |
| Monitoring | psutil, HTTPX |
| Log Processing | Drain3 |
| Frontend | HTML, CSS, JavaScript |
| Machine Learning | PyTorch (planned), TCN (planned) |
| Experiment Tracking | MLflow (planned) |
| Model Inference | ONNX Runtime (planned) |
| Migrations | Alembic |
| Testing | Pytest, HTTPX |
| Deployment | Docker, Docker Compose (planned) |

## Run Locally

### 1. Clone the repository

```powershell
git clone https://github.com/AyushAgrawal18/CloudGuardian.git
cd CloudGuardian
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

### 3. Install dependencies

```powershell
& ".\\.venv\\Scripts\\python.exe" -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=YOUR_POSTGRESQL_CONNECTION_STRING
JWT_SECRET_KEY=YOUR_SECRET_KEY
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Keep credentials and secrets private.

### 5. Apply database migrations

```powershell
& ".\\.venv\\Scripts\\python.exe" -m alembic upgrade head
```

### 6. Start the backend

```powershell
& ".\\.venv\\Scripts\\python.exe" -m uvicorn backend.app.main:app --reload
```

Open:

- Dashboard: http://127.0.0.1:8000/dashboard/
- API Documentation: http://127.0.0.1:8000/docs
- Health Check: http://127.0.0.1:8000/health

## Run the Monitoring Agent

Configure the agent variables in `.env`:

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
& ".\\.venv\\Scripts\\python.exe" -m agent.main
```

The agent periodically collects system metrics, stores them in a local SQLite queue, and sends pending metrics to the backend. If the backend becomes unavailable, queued metrics are retried after connectivity is restored.

## Log Processing

CloudGuardian uses Drain3 for online log parsing and template mining.

The log-processing pipeline:

1. Receives log messages through the authenticated REST API.
2. Validates that the associated host exists and is active.
3. Redacts common credentials and bearer tokens.
4. Uses Drain3 to identify log patterns and assign cluster IDs.
5. Stores log templates and individual log events in PostgreSQL.
6. Maintains host-specific Drain3 state.

Example request:

```http
POST /api/v1/logs
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

```json
{
  "host_id": "YOUR_REGISTERED_HOST_ID",
  "severity": "ERROR",
  "message": "Database connection timeout"
}
```

Supported severity levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

Log ingestion requires an ADMIN or OPERATOR account.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register a user |
| POST | `/api/v1/auth/login` | Authenticate a user |
| POST | `/api/v1/hosts` | Register a host |
| GET | `/api/v1/hosts` | List registered hosts |
| GET | `/api/v1/hosts/{host_id}` | Get host details |
| PATCH | `/api/v1/hosts/{host_id}` | Update host |
| DELETE | `/api/v1/hosts/{host_id}` | Deactivate host |
| POST | `/api/v1/metrics` | Ingest metrics |
| GET | `/api/v1/metrics` | Retrieve metrics |
| GET | `/api/v1/metrics/hosts` | Get host health |
| GET | `/api/v1/metrics/anomalies` | Retrieve anomalies |
| POST | `/api/v1/logs` | Ingest and process logs |

Protected endpoints require a valid JWT access token. Access permissions depend on the assigned role.

## Run Tests

```powershell
& ".\\.venv\\Scripts\\python.exe" -m pytest -q
```

## Project Structure

```text
CloudGuardian/
├── agent/
│   ├── collectors/
│   ├── core/
│   ├── storage/
│   ├── config.py
│   └── main.py
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── migrations/
│   │   └── versions/
│   └── data/
│
├── frontend/
│   └── index.html
├── tests/
├── alembic.ini
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

Runtime data under `backend/data/` is generated locally and should not be committed.

## Security Notes

- Keep `.env`, database files, passwords, and JWT secrets out of version control.
- Use strong, unique secrets for JWT signing.
- Assign users only the permissions they require.
- Keep monitoring-agent credentials private.
- Redact sensitive information before storing log messages.

## Research Objective

The long-term objective of CloudGuardian is to develop an AI-powered predictive maintenance platform that combines infrastructure metrics and log sequences to forecast potential failures, estimate system risk, and provide explainable alerts.

The project will be evaluated against conventional threshold-based, statistical, log-based, and multimodal detection approaches.