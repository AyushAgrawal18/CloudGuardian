# CloudGuardian

CloudGuardian is an infrastructure health monitoring and anomaly detection platform built with FastAPI and PostgreSQL. It collects server metrics, monitors registered hosts, detects threshold-based and statistical anomalies, and provides APIs for infrastructure management with JWT authentication and role-based access control.

## Run locally

From the repository root:

```powershell
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/cloudguardian
JWT_SECRET_KEY=YOUR_SECRET_KEY
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Run database migrations:

```powershell
& ".\.venv\Scripts\python.exe" -m alembic upgrade head
```

Start the application:

```powershell
& ".\.venv\Scripts\python.exe" -m uvicorn backend.app.main:app --reload
```

Open the dashboard at `http://127.0.0.1:8000/dashboard/` or the API documentation at `http://127.0.0.1:8000/docs`.

## API example

Metric ingestion requires a registered, active host and an Admin or Operator JWT token.

```powershell
$headers = @{
    Authorization = "Bearer YOUR_ACCESS_TOKEN"
}

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/metrics" `
    -Headers $headers `
    -ContentType "application/json" `
    -Body '{"host_id":"server-01","cpu_percent":35,"memory_percent":40,"disk_percent":45,"latency_ms":80,"error_rate_percent":0.5,"active_connections":20,"request_rate":100,"network_rtt_ms":25}'
```

Useful endpoints:

- `POST /api/v1/auth/register` - register a user
- `POST /api/v1/auth/login` - authenticate and obtain JWT
- `POST /api/v1/hosts` - register a host (Admin)
- `GET /api/v1/hosts` - list registered hosts
- `PATCH /api/v1/hosts/{host_id}` - update host details (Admin)
- `DELETE /api/v1/hosts/{host_id}` - deactivate a host (Admin)
- `POST /api/v1/metrics` - ingest a metric snapshot
- `GET /api/v1/metrics` - retrieve historical metrics
- `GET /api/v1/metrics/hosts` - show host health
- `GET /api/v1/metrics/anomalies` - retrieve detected anomalies

## Tests

```powershell
& ".\.venv\Scripts\python.exe" -m pytest -q
```

Current test status: **40 tests passing**.

## Roadmap

- [x] PostgreSQL integration and database migrations
- [x] JWT authentication and role-based access control
- [x] Host management APIs
- [x] Host-aware metric ingestion
- [x] Threshold-based anomaly detection
- [x] Statistical anomaly detection
- [ ] Automated monitoring agent
- [ ] Real-time metric collection and simulation
- [ ] ML-based resource utilization forecasting
- [ ] Predictive failure-risk analysis