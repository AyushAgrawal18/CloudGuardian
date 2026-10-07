# CloudGuardian

CloudGuardian is a basic infrastructure health monitor. The current MVP accepts server metrics,
stores them in SQLite, flags values above configured thresholds, and presents host status and
recent anomalies in a small dashboard.

## Run locally

From the repository root:

```powershell
python -m pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

Open the dashboard at `http://127.0.0.1:8000/dashboard/` or the API documentation at
`http://127.0.0.1:8000/docs`.

The SQLite database is created at `backend/cloudguardian.db`. Set `CLOUDGUARDIAN_DB_PATH` to
change its location.

## API example

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/metrics `
	-ContentType "application/json" `
	-Body '{"host_id":"host-1","cpu_percent":35,"memory_percent":40,"disk_percent":45,"latency_ms":80,"error_rate_percent":0.5,"active_connections":20,"request_rate":100,"network_rtt_ms":25}'
```

Useful endpoints:

- `POST /api/v1/metrics` - store a metric snapshot
- `GET /api/v1/metrics` - list recent snapshots
- `GET /api/v1/metrics/hosts` - show host health
- `GET /api/v1/metrics/anomalies` - list threshold breaches

## Tests

```powershell
pytest
```
