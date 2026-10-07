CloudGuardian Project Context
=============================

Project purpose
---------------
CloudGuardian is currently a basic infrastructure health monitoring MVP. It accepts
server metric snapshots, stores them in SQLite, detects values above configured
thresholds, supports host and time-range filtering, and displays host health and
recent anomalies in a small dashboard.

The project is being developed incrementally toward an AI-powered predictive
maintenance and anomaly detection platform.


Current implementation
----------------------
- FastAPI backend in backend/app.
- POST /api/v1/metrics stores a metric snapshot.
- GET /api/v1/metrics returns recent snapshots ordered by timestamp.
- GET /api/v1/metrics supports host filtering using host_id.
- GET /api/v1/metrics supports time-range filtering using start_time and end_time.
- GET /api/v1/metrics/hosts returns healthy, warning, or critical host status.
- GET /api/v1/metrics/anomalies returns detected threshold breaches.
- SQLite persistence is implemented in backend/app/services/metrics_service.py.
- The default database path is backend/cloudguardian.db.
- CLOUDGUARDIAN_DB_PATH can override the database location.
- Monitoring thresholds are centralized in backend/app/core/config.py.
- Threshold values can be configured through environment variables in .env.
- The dashboard is served at /dashboard/ from frontend/index.html.
- API documentation is available at /docs when the server is running.
- Automated MVP tests are in tests/test_mvp.py.
- Current automated test result: 2 tests passed.


Run locally
-----------
From the repository root:

    python -m pip install -r requirements.txt
    uvicorn backend.app.main:app --reload

Then open:

    http://127.0.0.1:8000/dashboard/

API documentation:

    http://127.0.0.1:8000/docs


Run tests
---------
From the repository root:

    python -m pytest -q

Current result:

    2 passed


Current anomaly rules
---------------------
- CPU usage: warning at 85 percent.
- Memory usage: warning at 85 percent.
- Disk usage: warning at 90 percent.
- Latency: warning at 500 ms.
- Error rate: warning at 5 percent.
- Network RTT: warning at 250 ms.
- A value at least 15 percent above its threshold is marked critical.
- Thresholds can be configured through environment variables.


Current filtering
-----------------
The metrics endpoint supports:

- Host filtering using host_id.
- Start-time filtering using start_time.
- End-time filtering using end_time.
- Combined host and time-range filtering.

Examples:

    GET /api/v1/metrics?host_id=host-1

    GET /api/v1/metrics?start_time=...&end_time=...

    GET /api/v1/metrics?host_id=host-1&start_time=...&end_time=...


Configuration
-------------
Threshold configuration is stored in:

    backend/app/core/config.py

Environment variables:

    CPU_THRESHOLD=85
    MEMORY_THRESHOLD=85
    DISK_THRESHOLD=90
    LATENCY_THRESHOLD=500
    ERROR_RATE_THRESHOLD=5
    NETWORK_RTT_THRESHOLD=250
    CRITICAL_MULTIPLIER=1.15

The .env file must remain untracked and must never be committed to GitHub.


Storage
-------
The current MVP uses SQLite.

Default database:

    backend/cloudguardian.db

CLOUDGUARDIAN_DB_PATH can be used to override the database location.

PostgreSQL has been installed and the connection has been successfully tested during
development, but PostgreSQL is NOT currently used by the active metrics service.

PostgreSQL/SQLAlchemy migration is planned for a later phase.


Development phases
------------------
Phase 1 — Basic MVP
Status: COMPLETE

- FastAPI backend.
- Metric ingestion.
- SQLite persistence.
- Threshold-based anomaly detection.
- Host health status.
- Anomaly listing.
- Basic dashboard.
- Swagger documentation.
- Automated tests.


Phase 2 — MVP Improvements
Status: COMPLETE

- Centralized threshold configuration.
- Environment-based threshold configuration.
- Host filtering.
- Time-range filtering.
- Combined host and time-range queries.
- Existing tests remain passing.


Phase 3 — Statistical Anomaly Detection
Status: NEXT

Planned:

- Rolling mean.
- Rolling standard deviation.
- Z-score.
- EWMA.
- Statistical anomaly scoring.

The existing threshold-based detection will remain.


Phase 4 — Advanced Storage and Security
Status: PLANNED

Planned:

- PostgreSQL.
- SQLAlchemy.
- Improved time-series storage.
- Authentication.
- Authorization.
- Role-based access control.
- API protection.
- Production configuration.
- Structured logging.
- Better database queries.


Phase 5 — Machine Learning and Predictive Maintenance
Status: PLANNED

Planned:

- Feature engineering.
- Classical ML baseline.
- Time-series models.
- Anomaly prediction.
- Failure probability.
- Predictive time-to-failure.
- Model confidence and calibration.


Phase 6 — Full SRS Implementation
Status: PLANNED

Planned:

- Prometheus metrics ingestion.
- Log ingestion.
- Drain3 log parsing.
- Kafka or Redis Streams.
- Advanced feature engineering.
- ML inference.
- Calibration.
- False Discovery Rate control.
- Drift detection.
- Explainable AI.
- Root-cause analysis.
- WebSockets.
- Authentication and RBAC.
- Full React dashboard.
- External alerts.
- Evaluation using public datasets.
- Chaos testing and fault injection.
- Production-oriented architecture.


Intentional MVP scope
---------------------
The current version does not implement the full SRS.

The following are future work:

- Log ingestion.
- Machine-learning models.
- Predictive time-to-failure.
- Calibration.
- Authentication.
- WebSockets.
- External alerts.
- Advanced storage.
- Chaos testing.
- Full React dashboard.
- Advanced explainability.

The MVP intentionally uses simple threshold detection so the complete data flow is
working, tested, reproducible, and easy to understand before advanced functionality
is introduced.


Security and publishing notes
-----------------------------
- No passwords, API keys, tokens, or private credentials belong in this repository.
- Keep local environment files and database files untracked.
- .gitignore excludes local environment and database files.
- External alerting and LLM integrations are not configured in the MVP.
- Before adding integrations, use environment variables or a secret manager.
- Never commit PostgreSQL credentials.
- Do not expose the development API publicly before authentication and security
  controls are implemented.


Suggested next work
-------------------
1. Add rolling-statistics anomaly scoring.
2. Add Z-score and EWMA based anomaly detection.
3. Keep threshold-based detection alongside statistical detection.
4. Add authentication before exposing the API outside a local environment.
5. Evaluate migration from SQLite to PostgreSQL.
6. Add machine-learning based failure prediction.
7. Expand toward the SRS only after the MVP remains tested and reproducible.


Current project status
----------------------
Phase 1 — Basic MVP:                    COMPLETE
Phase 2 — MVP Improvements:             COMPLETE
Phase 3 — Statistical Detection:        NEXT
Phase 4 — Storage and Security:         PLANNED
Phase 5 — ML and Predictive Maintenance: PLANNED
Phase 6 — Full SRS Implementation:      PLANNED

Overall progress:

    2 / 6 major phases completegit add PROJECT_CONTEXT.md