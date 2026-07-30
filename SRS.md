# Software Requirements Specification

**CloudGuardian** — Predictive Maintenance & Anomaly Detection in Cloud/Server Logs

| Field | Value |
|---|---|
| Document ID | CG-SRS-001 |
| Version | 1.0 |
| Date | 2026-07-30 |
| Status | Draft for review |
| Standard | IEEE 830-1998 §5 outline; requirement-quality rules per ISO/IEC/IEEE 29148:2018 |
| Scope | Ingestion, ML pipeline, calibration, explainability, dashboard, chaos testbed |
| Change control | IDs are permanent. Any change to a `M`-priority requirement requires a version bump and a note in §11.5 |

---

## Table of contents

1. [Introduction](#1-introduction)
2. [Overall description](#2-overall-description)
3. [Data requirements](#3-data-requirements)
4. [Functional requirements](#4-functional-requirements)
5. [Model requirements](#5-model-requirements)
6. [Evaluation requirements](#6-evaluation-requirements)
7. [External interface requirements](#7-external-interface-requirements)
8. [Non-functional requirements](#8-non-functional-requirements)
9. [Verification and acceptance](#9-verification-and-acceptance)
10. [Traceability](#10-traceability)
11. [Appendices](#11-appendices)

---

## Document conventions

**Modal verbs.** *shall* = binding, verified at acceptance. *should* = recommended; any omission
must be justified in the closure report. *may* = optional. Prose that is neither is marked
*Rationale:* and is non-binding.

**Requirement format.** Every requirement has a permanent ID, a priority, one verifiable
statement, a verification method, and a numeric or binary acceptance criterion. IDs are never
reused; withdrawn requirements are retained and marked `[WITHDRAWN]`.

**Priority (MoSCoW).** `M` Must — release blocker · `S` Should — high value, omissible under
schedule pressure with justification · `C` Could — stretch · `W` Won't — recorded to bound scope.

**Verification method.** `T` Test (automated, in CI where possible) · `A` Analysis (computed from
logged experiment artefacts) · `D` Demonstration (live, observed) · `I` Inspection (code, config
or document review).

---

## 1. Introduction

### 1.1 Purpose

This document specifies the complete functional, data, model, evaluation and quality requirements
for **CloudGuardian**, an AI-based predictive maintenance and anomaly detection system for cloud
and server infrastructure. It is the contractual baseline against which the system is designed,
implemented, verified and accepted.

Intended readership:

| Reader | Uses this document to |
|---|---|
| Developer / implementer | Derive design and code; every module traces to a requirement ID |
| Evaluator / examiner / reviewer | Judge completeness and check acceptance criteria objectively |
| Test engineer | Derive the test suite; §9 maps each requirement to a verification method |
| Project supervisor | Track scope, priority and progress against §10 traceability |

### 1.2 Scope

**Product name:** CloudGuardian.

**What it does.** CloudGuardian ingests structured system metrics and unstructured server logs
from monitored hosts, and produces (a) a calibrated probability that a host will fail within a
configurable prediction horizon, (b) an estimated time-to-failure, (c) a ranked, evidence-grounded
explanation naming the responsible metrics and log templates, and (d) alerts delivered to a
real-time dashboard and to external channels under a *statistically bounded false-alarm budget*.

**What it replaces.** Static threshold monitoring (for example "alert when CPU > 90%"), which
cannot read log text, cannot explain itself, fires constantly, and reports failures only after
they occur.

**Benefits and objectives.** The system exists to satisfy five stated project objectives, carried
here verbatim as objectives `OBJ-1` … `OBJ-5` and traced in §10.1:

| ID | Objective |
|---|---|
| OBJ-1 | Develop an AI-based predictive maintenance system |
| OBJ-2 | Process both structured system metrics and unstructured server logs |
| OBJ-3 | Predict potential failures before they occur |
| OBJ-4 | Provide explainable AI-based root cause analysis |
| OBJ-5 | Build a real-time dashboard for monitoring, visualization and alerts |

**Out of scope.** Recorded explicitly to bound the work; each is a `W` priority in §4–§8:

- Automated remediation. CloudGuardian recommends; it never restarts, scales, or reconfigures a
  monitored system. *Rationale:* an autonomous actuator driven by a probabilistic model can amplify
  an incident, and the blast radius is not justifiable for this deliverable.
- Distributed-trace ingestion (OpenTelemetry spans). Metrics and logs only.
- Multi-tenant SaaS operation, billing, quota enforcement.
- Agent-side collection software. CloudGuardian consumes from Prometheus and a log shipper; it
  does not ship its own host agent.
- Security intrusion detection. Faults in scope are reliability faults, not adversarial ones.

### 1.3 Definitions, acronyms and abbreviations

| Term | Definition |
|---|---|
| **Tick** | One discrete observation interval, Δ. Default Δ = 30 s. All windows are integer tick counts |
| **Window** | The lookback tensor at tick *t*: L consecutive ticks of metrics plus the log lines in that span. Default L = 60 ticks (30 min) |
| **Horizon H** | The forward span over which failure is predicted. `risk` at *t* answers: will a failure begin in (t, t+H]? |
| **Lead time** | failure_onset − alert_timestamp. The system's operational value. Negative or sub-δ lead time is a detection, not a prediction |
| **δ (min actionable lead)** | Smallest lead time counted as a successful prediction. Default δ = 120 s |
| **Precursor phase** | Interval [precursor_start, onset) during which a fault is developing but the service is still healthy. The only interval in which prediction is possible |
| **Failure / onset** | Timestamp at which a monitored service violates its SLO or terminates abnormally. Ground truth, not model output |
| **Template** | A log message with variable parts abstracted, e.g. `pool timeout acquiring connection after <*> ms`. Produced by the parser |
| **Template ID** | Stable integer key for a template, used for cache lookup and sequence encoding |
| **Novelty rate** | Fraction of lines in a window whose template was unseen during training. Operationally distinct from anomaly |
| **Reconstruction error** | ‖x − x̂‖ from an autoencoder trained on normal data only; the unsupervised anomaly score |
| **Conformal p-value** | Calibrated tail probability of a score under the normal distribution, computed from a held-out clean calibration set. Comparable across hosts and models; a raw score is not |
| **FDR** | False Discovery Rate — expected proportion of raised alerts that are false. The quantity the alert gate bounds |
| **Point adjustment (PA)** | An evaluation protocol that marks a whole anomalous range detected if any point in it is flagged. Inflates F1 to near 1.0 for random scores; prohibited as a headline metric by `EV-8` |
| **PR-AUC** | Area under the precision–recall curve. Primary point-level metric under class imbalance |
| **PATE / VUS-PR** | Range-aware evaluation metrics that credit temporally proximate detections without PA's inflation |
| **Alerts per host-day** | Count of alerts raised per monitored host per 24 h at a fixed recall. The primary false-alarm metric |
| **TTF** | Time to failure, estimated by the hazard head as a distribution, reported as p50 and p90 |
| **Drift** | Change in the input or score distribution that invalidates the trained model or its calibration |
| **Chaos injector** | Testbed component that induces a known fault at a known time with a known precursor ramp, writing ground truth |
| **SHAP** | Shapley Additive exPlanations — per-feature attribution of a model output |
| **Counterfactual** | A re-run of the model with one channel replaced by its baseline, reporting the resulting risk change |
| **Drain3** | Streaming log-template mining algorithm; the parser used by `FR-PARSE-1` |
| **ONNX** | Open Neural Network Exchange — the portable format used for CPU inference serving |
| **SLO** | Service Level Objective — the numeric threshold whose violation defines a failure |
| **MTTD** | Mean time to detect |

### 1.4 References

| Ref | Source |
|---|---|
| R1 | IEEE 830-1998, *Recommended Practice for Software Requirements Specifications* |
| R2 | ISO/IEC/IEEE 29148:2018, *Requirements engineering* |
| R3 | Landauer et al., *A Critical Review of Common Log Data Sets Used for Evaluation of Sequence-based Anomaly Detection Techniques*, arXiv:2309.02854 |
| R4 | Kim et al., *Towards a Rigorous Evaluation of Time-series Anomaly Detection*, AAAI 2022, arXiv:2109.05257 |
| R5 | *Did We Actually Fix It? Adversarial Stress-Test of Post-Point-Adjustment Metrics*, arXiv:2607.11969 |
| R6 | Jia et al., *Loghub-2.0 / A Large-Scale Evaluation for Log Parsing Techniques*, ISSTA 2024, arXiv:2308.10828 |
| R7 | Jacob et al., *Exathlon: A Benchmark for Explainable Anomaly Detection over Time Series*, VLDB 2021 |
| R8 | Su et al., *OmniAnomaly / Server Machine Dataset*, KDD 2019 |
| R9 | Le & Zhang, *NeuralLog: Log-based Anomaly Detection Without Log Parsing*, arXiv:2108.01955 |
| R10 | Zhang et al., *LogRobust*, ESEC/FSE 2019 |
| R11 | Du et al., *DeepLog*, CCS 2017 |
| R12 | He et al., *Drain: An Online Log Parsing Approach*, ICWS 2017; Drain3 implementation |
| R13 | *A Comparative Study of Semantic Log Representations*, arXiv:2604.08028 |
| R14 | *Are GNNs Actually Effective for Multimodal Fault Diagnosis?* (DiagMLP), arXiv:2501.02766 |
| R15 | *Conformal Anomaly Detection in Event Sequences*, ICML 2025 |
| R16 | *Context-Aware Online Conformal Anomaly Detection with FDR control*, arXiv:2505.01783 |
| R17 | Ghorbani et al., *PATE: Proximity-Aware Time series anomaly Evaluation* |
| R18 | Boniol et al., *VUS: Effective and Efficient Accuracy Measures for Time-Series AD*, VLDBJ 2025 |
| R19 | OWASP ASVS 4.0 — authentication and access-control controls referenced by §8.3 |
| R20 | CG-PLAN-001, CloudGuardian implementation plan (companion document) |

### 1.5 Overview

§2 gives system context, actors, constraints and assumptions. §3 specifies data sources, labels
and the leakage rules that make the predictive claim valid. §4 gives functional requirements by
subsystem. §5 specifies models and the baseline ladder. §6 specifies the evaluation protocol —
unusually detailed here, because in this problem domain a plausible-looking metric can be
inflated to near-1.0 by a random model (R4, R5), so the protocol *is* a requirement. §7 gives
interfaces, §8 non-functional requirements, §9 the acceptance procedure, §10 traceability.

---

## 2. Overall description

### 2.1 Product perspective

CloudGuardian is a new, self-contained system. It is not a replacement for an existing codebase,
but it is positioned as a replacement for threshold-based alerting rules in the monitoring stack
it attaches to. It sits downstream of a metrics store and a log shipper and upstream of the
on-call engineer.

```
   MONITORED ESTATE                CLOUDGUARDIAN                     CONSUMERS
 ┌───────────────────┐      ┌──────────────────────────────┐     ┌────────────────┐
 │ hosts, containers │      │ INGEST   parse · redact ·    │     │ dashboard      │
 │ app · db · cache  │──┬──▶│          window · featurize  │     │  (browser)     │
 │ node_exporter     │  │   ├──────────────────────────────┤     ├────────────────┤
 │ JSON app logs     │  │   │ INFER    AE · TCN · risk ·   │────▶│ on-call        │
 └───────────────────┘  │   │          hazard heads        │     │  engineer      │
 ┌───────────────────┐  │   ├──────────────────────────────┤     ├────────────────┤
 │ CHAOS TESTBED     │  │   │ CALIBRATE conformal p ·      │     │ Slack /        │
 │ (dev & eval only) │──┘   │           online FDR gate    │     │  webhook       │
 │ + ground truth    │      ├──────────────────────────────┤     ├────────────────┤
 └───────────────────┘      │ EXPLAIN  attribution ·       │     │ evaluation     │
 ┌───────────────────┐      │          counterfactual ·    │     │  artefacts     │
 │ PUBLIC DATASETS   │─────▶│          retrieval · brief   │     │  (report)      │
 │ HDFS BGL SMD Exa. │      ├──────────────────────────────┤     └────────────────┘
 │ (offline replay)  │      │ STORE  timeseries · incidents│
 └───────────────────┘      │        · vectors             │
                            └──────────────────────────────┘
```

Three ingestion modes share one pipeline, which is a hard design constraint: an offline replay of a
public dataset and a live stream from the testbed shall traverse identical parsing, featurization
and inference code, so that reported offline numbers are valid statements about the deployed
system. This is enforced by `FR-ING-5`.

### 2.2 Product functions — summary

| # | Function | Requirements |
|---|---|---|
| F1 | Ingest metrics and logs from live streams or dataset replay | §4.1 |
| F2 | Parse unstructured logs into stable templates; redact secrets | §4.2 |
| F3 | Build aligned metric+log feature windows | §4.3 |
| F4 | Score each window: reconstruction, forecast residual, risk, TTF | §4.4, §5 |
| F5 | Convert scores to calibrated p-values; gate alerts under an FDR budget | §4.5 |
| F6 | Detect drift; recalibrate; flag model degradation | §4.6 |
| F7 | Explain each alert: attribution, counterfactual, localization, narrative | §4.7 |
| F8 | Persist metrics, scores, alerts, incidents, feedback | §4.8 |
| F9 | Serve REST + WebSocket API with authentication and RBAC | §4.9, §7.2 |
| F10 | Present a real-time dashboard: fleet, host, incident, model-health views | §4.10, §7.1 |
| F11 | Deliver external alerts; accept confirm/dismiss feedback | §4.11 |
| F12 | Reproducibly evaluate all models under the §6 protocol | §4.12, §6 |
| F13 | Operate a chaos testbed that injects faults and writes ground truth | §4.13 |

### 2.3 User classes and characteristics

| Actor | Frequency | Expertise | Needs | Cares most about |
|---|---|---|---|---|
| **On-call engineer** (primary) | Continuous, interrupt-driven | High ops, low ML | Trustworthy alerts with enough context to act inside 60 s | Precision. A false page at 03:00 destroys trust permanently |
| **SRE / platform owner** | Weekly | High ops, medium ML | Fleet trends, alert-budget tuning, recall/precision trade-off | Alerts per host-day; whether the model is still calibrated |
| **ML engineer** (you) | Daily during build | High ML | Reproducible experiments, ablation tables, drift diagnostics | Honest metrics; no leakage |
| **Evaluator / examiner** | Once, at assessment | High ML, no system context | To verify claims independently | Whether numbers survive scrutiny; §6 and §9 |
| **Administrator** | Rarely | High ops | User and role management, retention config | Access control, secret hygiene |

*Rationale for the primary-actor choice:* the on-call engineer's precision requirement is what
makes §4.5 (calibrated alert gating) a `M` requirement rather than a `C`. A system with excellent
recall and 47 alerts/host-day would be switched off in week one, which would satisfy every ML
metric and fail the actual objective.

### 2.4 Operating environment

| Layer | Specification |
|---|---|
| OS | Linux, kernel ≥ 5.15 (developed on 6.8) |
| Runtime | Python 3.11; Node.js ≥ 20 for the dashboard build |
| Containers | Docker ≥ 24, Docker Compose v2 |
| ML | PyTorch ≥ 2.2 (training), ONNX Runtime ≥ 1.17 (serving) |
| Parsing | Drain3 with persistent state |
| Transport | Kafka, or Redis Streams in the reduced-footprint profile |
| Stores | TimescaleDB or ClickHouse (timeseries); PostgreSQL (incidents, users); pgvector (embeddings) |
| API | FastAPI + Uvicorn; REST and WebSocket |
| Dashboard | React 18 + TypeScript, charting via Recharts or visx |
| Training hardware | 1 GPU ≥ 8 GB VRAM, or CPU-only with reduced batch size |
| **Serving hardware** | **CPU-only, 4 vCPU / 8 GB RAM.** Binding: all latency and throughput criteria in §8.1 are CPU-only numbers |
| Browser | Chromium ≥ 120, Firefox ≥ 120 |

*Rationale for CPU-only serving:* R13 identifies embedding-generation cost as the practical
blocker for BERT-based log representations under CPU deployment. Fixing CPU as the serving target
forces the template-embedding cache (`FR-PARSE-5`) to be a requirement rather than an
optimisation, and makes the reported efficiency numbers meaningful.

### 2.5 Design and implementation constraints

| ID | Constraint |
|---|---|
| CON-1 | Serving inference shall be CPU-only. No requirement may assume a GPU at inference time |
| CON-2 | The system shall never write to, restart, or reconfigure a monitored system. Read-only telemetry access; recommendations only |
| CON-3 | Log redaction shall occur before persistence, not at query time |
| CON-4 | LLM narrative generation shall be optional. All detection, calibration, attribution and dashboard functions shall work with no LLM API key and no network egress |
| CON-5 | Offline replay and live streaming shall share one featurization and inference code path |
| CON-6 | All dataset splits shall be chronological. Random shuffling of temporally ordered records is prohibited |
| CON-7 | Every model artefact shall be reproducible from a versioned config + data hash + seed |
| CON-8 | Third-party dependencies shall be pinned to exact versions |
| CON-9 | Public datasets shall be used under their published licences, with provenance recorded in §3.1 |
| CON-10 | The whole system shall start from a clean checkout with one documented command (`docker compose up`) |

### 2.6 Assumptions and dependencies

| ID | Assumption | If false |
|---|---|---|
| ASM-1 | Monitored hosts emit metrics at ≥ 1 sample per Δ, and logs with parseable timestamps | Windowing degrades; `FR-ING-4` gap handling limits damage |
| ASM-2 | Host clocks are synchronised within ±1 tick (30 s) | Metric/log alignment breaks; `FR-ING-3` shall detect and report skew |
| ASM-3 | Failures are preceded by an observable precursor phase of ≥ δ | Prediction is impossible by construction; the system degrades to detection and must report this honestly (`EV-5`) |
| ASM-4 | A clean, failure-free interval exists for calibration | Conformal validity is void; `FR-CAL-1` shall refuse to calibrate and say so |
| ASM-5 | Template vocabulary growth is bounded in normal operation | Novelty rate saturates; `FR-DRIFT-2` shall raise a drift event, not an anomaly alert |
| ASM-6 | Failures are rare (< 5% of ticks) | Class-balance handling in `MR-6` is unnecessary but harmless |
| ASM-7 | Public dataset labels are approximately correct | Per R3 they are known-imperfect; mitigated by `EV-3` (multiple label constructions) and `DR-6` |
| ASM-8 | Anthropic API reachable when LLM briefs are enabled | `CON-4` guarantees graceful degradation |

---

## 3. Data requirements

*This section is elevated to top level because the validity of every claim in §6 depends on it.
Per R3, the standard datasets in this field contain anomalies that are largely detectable without
sequence modelling, and per R4 the standard scoring protocol inflates random models to near-perfect
F1. Requirements DR-5 … DR-8 exist specifically to prevent those two failure modes.*

### 3.1 Data sources

| ID | Source | Role | Scale / notes | Pri |
|---|---|---|---|---|
| DR-1.1 | **HDFS** (Loghub, R6) | Log-sequence anomaly detection, session-level | 11,175,629 lines; 575,061 blocks; 16,838 anomalous (2.9%) | M |
| DR-1.2 | **BGL** (Loghub, R6) | Log AD **and failure prediction with real lead time** — per-line alert tags, timestamped, node-attributable | ~4.7M lines | M |
| DR-1.3 | **SMD** (R8) | Multivariate metric AD; carries per-dimension interpretation labels usable for explanation evaluation | 28 machines × 38 metrics | S |
| DR-1.4 | **Exathlon** (R7) | Multimodal AD **with ground-truth explanations** — the only public source that lets `EV-7` be computed independently of our own testbed | High-dimensional Spark traces | S |
| DR-1.5 | **Chaos testbed** (§4.13) | Live, aligned metrics+logs+labels with controllable precursor length; primary source for lead-time and explanation evaluation and for the live demo | ≥ 40 fault episodes across ≥ 8 fault classes | M |
| DR-1.6 | **Synthetic generator** | Controlled ablations: known SNR, known lead time, injectable template drift | Parameterised | C |
| DR-1.7 | Loghub-2.0 (R6) | Parser accuracy benchmarking only | 14 datasets, ~3.6M lines avg | C |

`DR-1.2` is called out deliberately: because BGL's alert tags are timestamped and attributable to
nodes, a genuine lead-time task can be constructed on *public* data, so the predictive claim does
not rest solely on our own testbed. Reviewers can reproduce it.

### 3.2 Ingested record schemas

**Metric sample** — `MR` denotes required:

| Field | Type | MR | Notes |
|---|---|---|---|
| `ts` | RFC 3339 timestamp, UTC | ✓ | |
| `host` | string | ✓ | Entity key for per-host modelling and alert dedup |
| `service` | string | | Enables service-level localization (§4.7 layer 2) |
| `metric` | string | ✓ | e.g. `mem_rss_bytes` |
| `value` | float64 | ✓ | NaN permitted, meaning "missing"; must not be silently zero-filled |
| `labels` | map<string,string> | | Prometheus labels |

**Log record:**

| Field | Type | MR | Notes |
|---|---|---|---|
| `ts` | RFC 3339 timestamp, UTC | ✓ | |
| `host` | string | ✓ | |
| `service` | string | | |
| `level` | enum {DEBUG,INFO,WARN,ERROR,FATAL} | | Absent → inferred, and the inference flagged |
| `message` | string | ✓ | Raw unstructured text |
| `fields` | map | | Pre-structured JSON fields, if the emitter provides them |

**Ground-truth fault episode** — written by the chaos injector, and the label schema public
datasets are mapped into:

| Field | Type | Notes |
|---|---|---|
| `episode_id` | string | Primary key |
| `fault_type` | enum | See §4.13 table |
| `target` | string | host and/or service |
| `precursor_start` | timestamp | When the fault begins developing |
| `onset` | timestamp | When the SLO is violated or the process dies — **the** failure time |
| `recovery` | timestamp | End of the failure interval |
| `true_channels` | list<string> | Metrics causally involved — ground truth for `EV-7` |
| `true_templates` | list<int> | Template IDs causally involved — ground truth for `EV-7` |
| `injection_params` | map | Ramp rate, magnitude — enables the precursor-strength sweep |

### 3.3 Labelling, splitting and leakage control

| ID | Requirement | Pri | V |
|---|---|---|---|
| DR-5 | The risk-head label at tick *t* shall be 1 if and only if an `onset` falls in (t, t+H]. Ticks inside the failure interval [onset, recovery] **shall be excluded from risk-head training and from lead-time evaluation**. *Rationale:* including them teaches the model to recognise an ongoing outage, which inflates every metric while making the reported lead time fictitious. This is the single most consequential requirement in the document | M | T, I |
| DR-6 | The "normal" training set for unsupervised heads shall exclude [precursor_start, recovery]. *Rationale:* if precursor windows are labelled normal, the autoencoder learns the precursor as normal and can never flag it — the model is trained to fail at its own task | M | T, I |
| DR-7 | All splits shall be chronological: train → calibration → test, in time order, with no overlap. For HDFS, blocks shall be ordered by first-line timestamp; random block splits shall be prohibited and the reason stated in the report | M | T, I |
| DR-8 | The calibration split shall contain no labelled anomaly and no precursor window, and shall be temporally *after* train and *before* test | M | T |
| DR-9 | An alert at *t* shall count as a true positive for onset *T* only if T − t ∈ [δ, H]. Alerts with lead time < δ shall be reported separately as "detections, not predictions" | M | T |
| DR-10 | Feature computation at tick *t* shall use no data with timestamp > t. Normalisation statistics shall be fitted on the training split only. A unit test shall verify this by feeding future-shifted data and asserting output invariance | M | T |
| DR-11 | Each prepared dataset shall be content-hashed; the hash shall be recorded in the experiment artefact alongside config and seed | M | T |
| DR-12 | Where public labels are ambiguous (notably BGL), ≥ 2 label constructions shall be evaluated (e.g. first alert tag vs. first FATAL) and sensitivity reported | S | A |
| DR-13 | Class imbalance shall be handled without duplicating positives across the train/test boundary; any resampling shall occur strictly inside the training split | M | T |

### 3.4 Retention and privacy

| ID | Requirement | Pri | V |
|---|---|---|---|
| DR-14 | Raw log text shall be redacted (§4.2) before persistence. Unredacted text shall not be written to disk or to any store | M | T, I |
| DR-15 | Retention shall be configurable per store: raw windows (default 7 d), scores (90 d), incidents and explanations (indefinite) | S | I |
| DR-16 | Ingested telemetry shall not be transmitted to any third-party endpoint except (a) the configured LLM provider, only when `CON-4` narrative generation is explicitly enabled, and (b) the configured alert webhook. Both shall be off by default | M | I, T |
| DR-17 | When LLM briefs are enabled, the evidence bundle sent shall contain only redacted templates, numeric features and metric names — never raw log lines, never credentials | M | T, I |

---

## 4. Functional requirements

### 4.1 Ingestion — `FR-ING`

| ID | Requirement | Pri | V |
|---|---|---|---|
| FR-ING-1 | The system shall ingest metric samples from Prometheus (remote-write or scrape) conforming to §3.2 | M | T |
| FR-ING-2 | The system shall ingest log records from a shipper (Vector or Fluent Bit) via Kafka or Redis Streams, accepting both JSON and plain-text lines | M | T |
| FR-ING-3 | The system shall align metrics and logs onto a common tick grid of width Δ (configurable, default 30 s), and shall detect and report clock skew > 1 tick between sources (per `ASM-2`) | M | T |
| FR-ING-4 | Missing metric samples shall be represented explicitly as missing and handled by a configured policy (forward-fill ≤ 2 ticks, then NaN + a `missing_fraction` feature). Silent zero-filling shall be prohibited. *Rationale:* zero-filling a gap manufactures a step change that reads as an anomaly | M | T |
| FR-ING-5 | The system shall provide a replay mode that reads a public dataset and emits records through the identical downstream pipeline as the live path, at configurable speed-up (per `CON-5`) | M | T, D |
| FR-ING-6 | Ingestion shall be idempotent and at-least-once safe: replaying the same offsets shall not duplicate windows or alerts | S | T |
| FR-ING-7 | The system shall expose ingestion lag and drop counters as its own metrics | S | T |
| FR-ING-8 | Ingestion shall apply per-host backpressure and shall degrade by sampling DEBUG-level lines before dropping WARN or above | S | T |

### 4.2 Parsing and redaction — `FR-PARSE`

| ID | Requirement | Pri | V |
|---|---|---|---|
| FR-PARSE-1 | The system shall parse each log line into a template and parameter list using Drain3 (R12) with persistent state, so template IDs are stable across restarts | M | T |
| FR-PARSE-2 | The system shall maintain a template registry: id, template text, first-seen, last-seen, count, embedding reference | M | T |
| FR-PARSE-3 | Redaction shall run **before** persistence and shall remove: IPv4/IPv6, emails, URLs with credentials, bearer/JWT tokens, AWS-style keys, private-key blocks, and high-Shannon-entropy parameter values above a configured threshold. Redacted spans shall be replaced with a typed placeholder, e.g. `<EMAIL>` | M | T |
| FR-PARSE-4 | Numeric parameters shall be extracted as typed features (e.g. latency from `took <*> ms`) and z-scored against a per-template baseline. *Rationale:* the template alone loses the magnitude, which is often the whole signal | S | T |
| FR-PARSE-5 | Each **template** shall be embedded once by a sentence encoder (MiniLM class) and cached keyed by template ID. The encoder shall not be invoked per log line. Cache hit rate and the resulting throughput gain shall be measured and reported (addresses the R13 CPU bottleneck) | M | T, A |
| FR-PARSE-6 | A previously unseen template shall be embedded on demand, assigned to its nearest cached neighbour in embedding space for model input (parser-free fallback per R9), **and** counted in the window's `novelty` feature | M | T |
| FR-PARSE-7 | Parser accuracy shall be reported on Loghub-2.0 ground-truth templates (grouping accuracy and parsing accuracy) | C | A |
| FR-PARSE-8 | Parsing throughput shall be ≥ 20,000 lines/s single-process on the reference CPU | S | T |

### 4.3 Windowing and featurization — `FR-FEAT`

| ID | Requirement | Pri | V |
|---|---|---|---|
| FR-FEAT-1 | The system shall build, per host per tick, a window of L ticks (default 60) containing the metric tensor and the log lines in span | M | T |
| FR-FEAT-2 | Log windows shall be represented in **three views simultaneously**: (a) ordered template-ID sequence, (b) template count vector, (c) cached template-embedding sequence. *Rationale:* sequence-only representations miss "too many retries"; count-only representations miss ordering. Requiring all three prevents a whole class of blind spot | M | T |
| FR-FEAT-3 | The following window-level log features shall be computed: severity histogram, novelty rate, template entropy, inter-arrival coefficient of variation (burstiness), log-volume rate, error ratio, per-template numeric-parameter z-scores | M | T |
| FR-FEAT-4 | The following metric features shall be computed per channel: raw value, first difference, rolling mean/std/min/max, slope over the window (least squares), EWMA residual, and missing fraction | M | T |
| FR-FEAT-5 | Both windowing strategies shall be supported and compared: fixed-size sliding windows (metrics + BGL) and session/identifier grouping (HDFS block ID) | M | T |
| FR-FEAT-6 | Feature specifications shall be declarative (YAML) and versioned; the feature-spec version shall be recorded in every artefact | S | I |
| FR-FEAT-7 | Featurization shall be deterministic: identical input yields byte-identical output for a fixed spec version | M | T |

### 4.4 Scoring and inference — `FR-INF`

| ID | Requirement | Pri | V |
|---|---|---|---|
| FR-INF-1 | For each window the system shall produce: reconstruction error (per channel and aggregate), forecast residual, risk = P(failure in (t, t+H]), and a TTF distribution summarised as p50 and p90 | M | T |
| FR-INF-2 | Log-sequence surprise −log p(template ᵢ \| context) shall be produced per line and aggregated per window | M | T |
| FR-INF-3 | H shall be configurable and evaluated over {2.5, 5, 10, 20} min | M | T, A |
| FR-INF-4 | Serving shall use ONNX Runtime on CPU; models shall be exported and the export verified to match PyTorch output within 1e-4 | M | T |
| FR-INF-5 | Inference shall be batched across hosts and shall meet the §8.1 latency budget | M | T |
| FR-INF-6 | Every scored window shall be persisted with its model version, feature-spec version and config hash | M | T |
| FR-INF-7 | The system shall support ≥ 2 concurrently-served model versions for shadow evaluation of a candidate against the incumbent | C | T |

### 4.5 Calibration and alert gating — `FR-CAL`

*This subsystem is the direct answer to the "high number of false alarms" problem, and is the
system's most defensible contribution. It converts an arbitrary threshold into a stated
statistical budget (R15, R16).*

| ID | Requirement | Pri | V |
|---|---|---|---|
| FR-CAL-1 | Raw scores shall be converted to conformal p-values using a clean calibration split (`DR-8`). If no valid calibration data exists, the system shall refuse to emit calibrated p-values and shall surface an explicit "uncalibrated" state rather than falling back silently to a raw threshold | M | T |
| FR-CAL-2 | Alerts shall be gated by an online FDR-controlling procedure (LORD-style) with a configurable target α (default 0.05) | M | T |
| FR-CAL-3 | The gate shall apply k-of-m hysteresis (default 3-of-5) so that a single-tick spike cannot raise an alert | M | T |
| FR-CAL-4 | The gate shall deduplicate per host with a configurable cooldown (default 600 s) and shall attach repeat evidence to the existing open incident instead of raising a new alert | M | T |
| FR-CAL-5 | The system shall expose the achieved alert rate as **alerts per host-day**, and shall let an operator set a target rate from which α is derived automatically | M | T, D |
| FR-CAL-6 | Severity shall be derived from the conformal p-value and predicted TTF, on a documented, monotone mapping | S | I |
| FR-CAL-7 | A cost-optimal operating point shall be computable from configured c_fp and c_miss and displayed on the cost curve | S | A |
| FR-CAL-8 | Alert gating decisions shall be logged with full inputs (p-value, wealth, hysteresis state) so any suppression can be explained after the fact. *Rationale:* an unexplainable suppression is worse than a false alarm — it destroys trust in the whole system | M | T |

### 4.6 Drift detection — `FR-DRIFT`

| ID | Requirement | Pri | V |
|---|---|---|---|
| FR-DRIFT-1 | The system shall monitor score-distribution drift (PSI and/or KL against the calibration distribution) and residual drift (ADWIN) | M | T |
| FR-DRIFT-2 | The system shall monitor template-vocabulary growth rate and shall raise a **drift event, not an anomaly alert**, when novelty rate exceeds its threshold. *Rationale:* a deploy legitimately creates new templates; conflating that with a fault is the single largest source of false alarms in production log monitoring | M | T |
| FR-DRIFT-3 | On confirmed drift the system shall recalibrate conformal quantiles on recent clean data and record the recalibration event | M | T |
| FR-DRIFT-4 | The dashboard shall display a model-health state ∈ {calibrated, degraded, uncalibrated} with the evidence behind it | M | D |
| FR-DRIFT-5 | The system shall emit a retraining recommendation when drift persists beyond a configured window. Retraining shall not be triggered automatically | S | T |

### 4.7 Explainability — `FR-XAI`

**Layer 1 — attribution (deterministic, always available):**

| ID | Requirement | Pri | V |
|---|---|---|---|
| FR-XAI-1 | Reconstruction error shall be decomposed per metric channel and the top-k contributors returned | M | T |
| FR-XAI-2 | SHAP attributions shall be computed for the risk head (DeepSHAP online; KernelSHAP permitted offline for the report) | M | T |
| FR-XAI-3 | Log attribution shall combine fusion-attention weight with per-template surprise to rank templates, returning for each: id, template text, window count, baseline count, surprise, and a redacted example line | M | T |
| FR-XAI-4 | Counterfactuals shall be produced by **actually re-running the model** with one channel replaced by its baseline (7-day median), reporting risk before and after. Estimated or interpolated counterfactuals shall not be presented as computed ones | M | T |
| FR-XAI-5 | Attribution shall complete within the §8.1 explanation latency budget | M | T |

**Layer 2 — localization:**

| ID | Requirement | Pri | V |
|---|---|---|---|
| FR-XAI-6 | Affected hosts/services shall be ranked by anomaly onset time (earliest ≈ likeliest origin) | M | T |
| FR-XAI-7 | Where topology is available, an anomaly-propagation graph shall be built and scored (PageRank-class) | S | T |
| FR-XAI-8 | Any graph-based localization shall be reported **alongside a topology-agnostic baseline**, and shall be claimed as beneficial only if it measurably beats that baseline. *Rationale:* R14 shows a minimal topology-agnostic MLP matches GNNs for multimodal fault diagnosis; an unbenchmarked graph claim is not credible | S | A |
| FR-XAI-9 | Causal screening (Granger/PCMCI) may be applied to the top-10 ranked channels only, with the scope limitation stated | C | A |

**Layer 3 — narrative:**

| ID | Requirement | Pri | V |
|---|---|---|---|
| FR-XAI-10 | The LLM shall act **only** as a narrator over the retrieved evidence bundle. It shall not perform detection, scoring, or thresholding | M | I |
| FR-XAI-11 | Briefs shall be schema-validated JSON. **Every claim shall cite an evidence id** from `top_metrics` or `top_templates`; uncited claims shall be rejected programmatically and the brief regenerated or withheld | M | T |
| FR-XAI-12 | When evidence is insufficient the brief shall return `insufficient_evidence` rather than speculate | M | T |
| FR-XAI-13 | Briefs shall be cached by evidence hash | S | T |
| FR-XAI-14 | Retrieval shall supply similar past incidents (vector similarity over explanation embeddings) and relevant runbook chunks, each with a similarity score | S | T |
| FR-XAI-15 | With LLM disabled, layers 1–2 shall render fully and the UI shall state that narrative generation is off (per `CON-4`) | M | T, D |

### 4.8 Storage — `FR-STORE`

| ID | Requirement | Pri | V |
|---|---|---|---|
| FR-STORE-1 | Metrics, features and scores shall be stored in a timeseries store with per-host per-tick query support | M | T |
| FR-STORE-2 | Incidents shall be stored relationally: alert, evidence bundle, explanation, operator feedback, resolution | M | T |
| FR-STORE-3 | Template and explanation embeddings shall be stored in a vector index supporting k-NN | S | T |
| FR-STORE-4 | Retention policies per `DR-15` shall be enforced by a scheduled job | S | T |
| FR-STORE-5 | Schema migrations shall be versioned and forward-only | S | I |

### 4.9 API — `FR-API`

| ID | Requirement | Pri | V |
|---|---|---|---|
| FR-API-1 | A REST API shall expose: fleet status, host detail, score history, incident list and detail, explanation bundle, model health, config | M | T |
| FR-API-2 | A WebSocket channel shall push new scores, alerts and drift events to subscribed clients | M | T |
| FR-API-3 | **All** REST and WebSocket endpoints shall require authentication (JWT or OIDC). No unauthenticated endpoint shall expose telemetry, log text, or template content. *Rationale:* the store contains aggregated production log content; an open browse endpoint is a data-exposure incident, not a convenience | M | T, I |
| FR-API-4 | RBAC shall enforce roles: viewer (read), operator (read + acknowledge/dismiss), admin (all + config + user management) | M | T |
| FR-API-5 | The API shall be rate-limited per principal | S | T |
| FR-API-6 | Requests shall be validated against typed schemas; validation failure shall return 4xx with a machine-readable error | M | T |
| FR-API-7 | An OpenAPI 3 specification shall be generated and served | S | T |
| FR-API-8 | All state-changing requests shall be recorded in an audit log with principal, action and timestamp | S | T |

### 4.10 Dashboard — `FR-UI`

| ID | Requirement | Pri | V |
|---|---|---|---|
| FR-UI-1 | **Fleet view:** all hosts with current risk, colour-coded severity, sortable by risk and by TTF; live-updating | M | D |
| FR-UI-2 | **Host view:** metric timeseries with anomaly score overlay, risk trace, TTF band, log-template timeline with novel templates visually distinguished | M | D |
| FR-UI-3 | **Incident view:** the full explanation — top metrics with SHAP values and baselines, top templates with counts and examples, counterfactual results, similar incidents, runbook chunks, narrative brief when enabled | M | D |
| FR-UI-4 | **Model-health view:** calibration state, drift indicators, alerts-per-host-day trend, recent recalibrations | M | D |
| FR-UI-5 | **Evaluation view:** lead-time distribution, alerts-per-host-day vs. recall, cost curve with the optimal point marked | S | D |
| FR-UI-6 | New alerts shall appear in the UI within 2 s of gate emission | M | T, D |
| FR-UI-7 | Operators shall be able to acknowledge, dismiss (with reason), and annotate an incident from the UI | M | D |
| FR-UI-8 | The UI shall visually distinguish "new template appeared" from "known anomalous pattern" everywhere both can occur (paired with `FR-DRIFT-2`) | M | D |
| FR-UI-9 | Charts shall meet WCAG 2.1 AA contrast, shall not encode meaning by colour alone, and shall be legible in light and dark themes | S | I |
| FR-UI-10 | The UI shall render a clear degraded state when the backend is unreachable, never a blank or stale-but-plausible screen | M | T |

### 4.11 Alerting and feedback — `FR-ALERT`

| ID | Requirement | Pri | V |
|---|---|---|---|
| FR-ALERT-1 | Alerts shall be deliverable to Slack and to a generic webhook, containing severity, host, risk, TTF, top-3 evidence items and a deep link | M | T |
| FR-ALERT-2 | Delivery shall retry with exponential backoff and shall record permanent failures | S | T |
| FR-ALERT-3 | Operator confirm/dismiss feedback shall be captured as labels for active learning | S | T |
| FR-ALERT-4 | Feedback shall never trigger automatic retraining; it shall enqueue a reviewed retraining candidate | M | I |
| FR-ALERT-5 | External delivery shall be disabled by default and require explicit configuration (per `DR-16`) | M | I |

### 4.12 Experiment harness — `FR-EXP`

| ID | Requirement | Pri | V |
|---|---|---|---|
| FR-EXP-1 | Every experiment shall be defined by a single YAML config: dataset, split, features, model, seed, metrics | M | I |
| FR-EXP-2 | Runs shall be tracked (MLflow) with params, metrics, artefacts, data hash, git SHA | M | T |
| FR-EXP-3 | `run_all.sh` shall reproduce every table and figure in the final report from a clean checkout | M | D |
| FR-EXP-4 | Every model shall be evaluated on ≥ 5 seeds; results reported as mean ± std | M | A |
| FR-EXP-5 | Model comparisons shall use a paired non-parametric test (Wilcoxon signed-rank) with the p-value reported | S | A |
| FR-EXP-6 | The harness shall compute every §6 metric family for every model in the §5.3 ladder without per-model special-casing | M | T |

### 4.13 Chaos testbed — `FR-TB`

| ID | Requirement | Pri | V |
|---|---|---|---|
| FR-TB-1 | The testbed shall run a multi-tier application under Docker Compose: reverse proxy → API service → relational DB + cache + background worker | M | D |
| FR-TB-2 | A load generator shall apply a realistic diurnal traffic profile with configurable noise | M | T |
| FR-TB-3 | The injector shall implement ≥ 8 fault classes, each with a **gradual precursor ramp** of configurable length. *Rationale:* an instantaneous fault is unpredictable by construction; without a ramp the predictive task is void | M | T, D |
| FR-TB-4 | Each injection shall write a ground-truth episode record per §3.2, including `true_channels` and `true_templates` | M | T |
| FR-TB-5 | Injection shall be reproducible from a seed and a scenario file | M | T |
| FR-TB-6 | The testbed shall support precursor-strength sweeps to produce a detection-rate vs. precursor-strength curve | S | A |
| FR-TB-7 | Teardown shall fully restore the baseline state; no fault shall persist across episodes | M | T |

**Fault classes (`FR-TB-3`):**

| Fault | Mechanism | Expected precursor signal |
|---|---|---|
| Memory leak → OOM | Worker allocates progressively | RSS slope, GC frequency, `MemoryWarning` templates |
| Disk exhaustion | `fallocate` ramp | Free-space slope, `ENOSPC` retry templates |
| Connection-pool exhaustion | Leak DB connections | Pool wait p99, `pool timeout` templates |
| Slow-query storm | Drop an index | Query latency tail, lock-wait log lines |
| Network degradation | `tc netem` delay/loss ramp | RTT variance, timeout/retry templates |
| CPU contention | `stress-ng` ramp | Steal time, run-queue depth |
| Cascading dependency failure | Kill a downstream service | Circuit-breaker templates, error-rate propagation |
| Config regression | Bad deploy | New templates appear, error-ratio step |

---

## 5. Model requirements

### 5.1 Formal task definition — `MR-1`

At tick *t*, given metrics X_t ∈ ℝ^(L×D) and log window W_t, the system shall produce:

| Head | Output | Trained on | Labels needed |
|---|---|---|---|
| 1. Reconstruction | s_rec = ‖X_t − X̂_t‖, per channel and total | Normal windows only (`DR-6`) | None |
| 2. Forecast | residual of X̂_(t+1:t+h) vs. actual | Normal windows | None |
| 3. Risk | r_t = P(∃ onset T ∈ (t, t+H] \| F_≤t) | Labelled windows (`DR-5`) | Yes |
| 4. Hazard | discrete-time TTF distribution → p50, p90 | Labelled windows | Yes |
| — | log surprise −log p(templateᵢ \| context) | Normal log sequences | None |

| ID | Requirement | Pri | V |
|---|---|---|---|
| MR-1 | The model shall implement all four heads with a shared encoder, jointly trained | M | T |
| MR-2 | Loss shall be L = λ₁·MSE(recon) + λ₂·MSE(forecast) + λ₃·Focal(risk) + λ₄·NLL(hazard), with supervised terms **masked where labels are absent**, so the model trains on unlabelled data and sharpens where labels exist | M | T, I |
| MR-3 | The metric encoder shall be a temporal convolutional network with dilations {1,2,4,8,16}, giving a receptive field ≥ L | M | I |
| MR-4 | The log encoder shall consume cached template embeddings; fusion shall be by cross-attention from metric tokens to log tokens, with attention weights retained and exposed for `FR-XAI-3` | M | T |
| MR-5 | Fusion shall be ablated across: metrics-only, logs-only, score-level (late) fusion, concatenation, cross-attention. Cross-attention shall be claimed as the contribution only if it beats late fusion by a margin exceeding seed variance (per R14) | M | A |
| MR-6 | Class imbalance shall be addressed by focal loss and, optionally, training-split-only resampling (`DR-13`); no synthetic positive shall cross the split boundary | M | T |
| MR-7 | Model size shall be ≤ 50 MB in ONNX form, to keep CPU serving within §8.1 | S | T |

### 5.2 Log representation — `MR-8`

| ID | Requirement | Pri | V |
|---|---|---|---|
| MR-8 | Template embeddings shall be produced by a sentence encoder and cached per template ID (`FR-PARSE-5`). Per-line encoder invocation shall be prohibited in the serving path | M | T, I |
| MR-9 | The three-view representation of `FR-FEAT-2` shall all reach the model; dropping any view shall be an explicit ablation, not a default | M | T |
| MR-10 | Unseen templates shall be handled by embedding-space nearest neighbour **and** counted in `novelty` — never silently mapped to a padding or unknown token that discards the signal | M | T |

### 5.3 Baseline ladder — `MR-11`

The comparison table is a primary deliverable, not supporting material. Rung 2 exists because R3
found trivial baselines competitive on these datasets; omitting it would leave the central claim
unfalsifiable.

| Rung | Method | Purpose | Pri |
|---|---|---|---|
| 1 | Static threshold (3σ, p99) | The incumbent system being replaced | M |
| 2 | Keyword / severity matcher | **The trivial baseline R3 shows beats deep models on HDFS** | M |
| 3 | STIDE / new-template detector | Tests whether "unseen event type" explains the labels | M |
| 4 | Isolation Forest, One-Class SVM, PCA | Classical unsupervised | M |
| 5 | ARIMA / Prophet residual | Classical forecasting | S |
| 6 | LSTM-AE, VAE | Standard deep reconstruction | M |
| 7 | DeepLog (R11), LogAnomaly, LogRobust (R10) | Published log-AD baselines | M |
| 8 | TCN forecaster; USAD / TranAD-class | Published metric-AD baselines | S |
| 9 | **CloudGuardian**, with the `MR-5` ablations | The contribution | M |

| ID | Requirement | Pri | V |
|---|---|---|---|
| MR-11 | All `M`-priority rungs shall be implemented and evaluated under the identical §6 protocol and identical splits | M | T, A |
| MR-12 | Where a rung matches or beats CloudGuardian on a dataset, this shall be reported prominently, not omitted. *Rationale:* the finding "on HDFS a keyword matcher is competitive, and here is why" is a stronger and more publishable result than a suppressed comparison | M | I |

---

## 6. Evaluation requirements

*Specified as requirements rather than left to the report because in this domain the choice of
metric can manufacture a result. R4 proves a random anomaly score reaches near-perfect F1 under
point adjustment; R5 finds some proposed replacements still inflatable. The protocol is therefore
part of the specification and is verified at acceptance.*

| ID | Requirement | Pri | V |
|---|---|---|---|
| EV-1 | **Point-level metrics** shall be reported: PR-AUC (primary), ROC-AUC, and F1 at a threshold selected on the validation split only. *Rationale:* at 2.9% positives ROC-AUC flatters; PR-AUC is the honest primary | M | A |
| EV-2 | **Range-aware metrics** shall be reported: range-based precision/recall, and PATE (R17) and/or VUS-PR (R18). Where VUS is used, VUS-**PR** shall be preferred over VUS-ROC, since R5 found VUS-ROC inflated on 131 series where VUS-PR was not | M | A |
| EV-3 | **Predictive metrics** shall be reported and shall constitute the headline result: (a) detection rate vs. horizon H curve; (b) lead-time distribution — median and full distribution, not mean alone; (c) **alerts per host-day at fixed recall levels {0.7, 0.8, 0.9}**; (d) cost curve over c_fp/c_miss with the optimal operating point marked | M | A |
| EV-4 | Alerts with lead time < δ shall be counted separately and labelled "detections, not predictions" (`DR-9`) | M | A |
| EV-5 | Where a fault class proves unpredictable (no observable precursor), this shall be stated per class rather than averaged away | M | A |
| EV-6 | **Robustness** shall be evaluated with degradation curves for: template drift (synthesised log-statement edits, R10 protocol), Gaussian metric noise, label noise, and randomly dropped metric channels | S | A |
| EV-7 | **Explanation quality** shall be measured, not asserted: precision@k and hit-rate@k of attributed channels and templates against `true_channels`/`true_templates`, on the testbed and on Exathlon (R7). A random-attribution baseline shall be reported alongside | M | A |
| EV-8 | Point-adjusted F1 **shall not be used as a headline metric**. It shall be reported once, in a dedicated figure, next to the point-adjusted F1 of a *random* scorer on the same data, to demonstrate why the protocol is rejected | M | A |
| EV-9 | **Efficiency** shall be reported on the reference CPU: lines/s parsing throughput, p50/p95/p99 inference latency per window, explanation latency, peak RSS, ONNX model size, and template-cache hit rate | M | T |
| EV-10 | All results shall be from ≥ 5 seeds, mean ± std (`FR-EXP-4`); single-run numbers shall not appear in the report | M | A |
| EV-11 | An ablation table shall isolate the contribution of: log modality, metric modality, fusion type, template embeddings vs. IDs, conformal gating vs. fixed threshold, and each of the four heads | M | A |
| EV-12 | A leakage audit shall be documented: the tests verifying `DR-5`–`DR-10`, with their results | M | T, I |

### 6.1 Target performance

Targets, not guarantees. Each is a hypothesis the acceptance run tests; a missed target is a
finding to report with analysis, not a defect to hide.

| Metric | Dataset | Target | Requirement |
|---|---|---|---|
| PR-AUC | HDFS (chronological split) | ≥ 0.90 | EV-1 |
| PR-AUC | BGL | ≥ 0.85 | EV-1 |
| Detection rate @ H = 10 min | Testbed | ≥ 0.85 | EV-3 |
| Median lead time | Testbed | ≥ 4 min | EV-3 |
| Alerts per host-day @ recall 0.90 | Testbed | ≤ 3 | EV-3 |
| Alerts per host-day @ recall 0.90 | 3σ baseline, same data | reported for contrast | EV-3 |
| Explanation precision@3 | Testbed + Exathlon | ≥ 0.70, and ≫ random baseline | EV-7 |
| p95 inference latency per window | Reference CPU | ≤ 100 ms | EV-9, NFR-1 |
| Alert-to-UI latency | End to end | ≤ 2 s | FR-UI-6 |

---

## 7. External interface requirements

### 7.1 User interfaces

Five views per `FR-UI-1`…`FR-UI-5`. Binding UI constraints:

- Live views shall update by WebSocket push, not polling.
- Every displayed number that is a model output shall be accompanied by its uncertainty (p-value,
  or TTF p50/p90 band) — a bare point estimate shall not be shown for a probabilistic quantity.
- Every alert shall be one click from its full evidence bundle.
- Colour shall never be the sole carrier of meaning (`FR-UI-9`).
- The degraded/disconnected state shall be visually unmistakable (`FR-UI-10`).

### 7.2 Software interfaces

| Interface | Direction | Protocol | Notes |
|---|---|---|---|
| Prometheus | inbound | HTTP remote-write / scrape | Metrics |
| Vector / Fluent Bit | inbound | Kafka or Redis Streams | Logs |
| Kafka / Redis Streams | internal | binary / RESP | Topics: `metrics`, `logs`, `scores`, `alerts` |
| TimescaleDB / ClickHouse | internal | SQL | Timeseries |
| PostgreSQL + pgvector | internal | SQL | Incidents, users, embeddings |
| ONNX Runtime | internal | in-process | CPU inference |
| Anthropic API | outbound, optional | HTTPS | Narrative briefs only; off by default (`CON-4`, `DR-16`) |
| Slack / webhook | outbound, optional | HTTPS | Alerts; off by default (`FR-ALERT-5`) |
| MLflow | internal | HTTP | Experiment tracking |

### 7.3 Hardware interfaces

None directly. All host telemetry arrives via the collectors in §7.2.

### 7.4 Communication interfaces

| ID | Requirement | Pri | V |
|---|---|---|---|
| CI-1 | REST over HTTPS; JSON bodies; RFC 3339 UTC timestamps throughout | M | T |
| CI-2 | WebSocket over WSS with token authentication performed **before** any subscription is honoured | M | T |
| CI-3 | All timestamps in transit and at rest shall be UTC. Local-time rendering shall occur in the browser only | M | T |
| CI-4 | API responses shall be versioned under a path prefix (`/api/v1`) | S | I |

---

## 8. Non-functional requirements

### 8.1 Performance — `NFR-1`…`NFR-8`

All figures are on the reference serving hardware of §2.4 (4 vCPU, 8 GB, **no GPU**).

| ID | Requirement | Target | Pri | V |
|---|---|---|---|---|
| NFR-1 | Inference latency per window, p95 | ≤ 100 ms | M | T |
| NFR-2 | Parsing throughput, single process | ≥ 20,000 lines/s | S | T |
| NFR-3 | End-to-end latency, log line arrival → alert in UI | ≤ 2 s p95 | M | T |
| NFR-4 | Explanation generation, layers 1–2 | ≤ 500 ms p95 | M | T |
| NFR-5 | Narrative brief, when enabled | ≤ 10 s p95, asynchronous, never blocking the alert | S | T |
| NFR-6 | Monitored hosts at reference sizing | ≥ 50 concurrent | S | T |
| NFR-7 | Peak resident memory, serving process | ≤ 4 GB | S | T |
| NFR-8 | Dashboard initial load | ≤ 3 s on a 10 Mbit link | S | T |

### 8.2 Reliability and availability

| ID | Requirement | Pri | V |
|---|---|---|---|
| NFR-9 | The scoring pipeline shall survive a restart without losing template state (persistent Drain3) or calibration state | M | T |
| NFR-10 | An ingestion outage shall not produce spurious alerts: on resumption the system shall detect the gap and suppress alerts until L ticks of continuous data are available. *Rationale:* a monitoring system that pages the on-call because it lost its own input is worse than useless | M | T |
| NFR-11 | Component failure shall degrade gracefully — vector-store unavailability shall disable similar-incident retrieval, not the alert | M | T |
| NFR-12 | No single component failure shall lose an already-raised alert; alerts shall be persisted before delivery is attempted | M | T |

### 8.3 Security

| ID | Requirement | Pri | V |
|---|---|---|---|
| NFR-13 | All API and WebSocket access shall be authenticated (`FR-API-3`); there shall be no unauthenticated telemetry or log-content endpoint | M | T, I |
| NFR-14 | RBAC shall be enforced server-side; client-side role checks shall not be the enforcement point | M | T |
| NFR-15 | Secrets shall be supplied by environment or secret store; no credential shall appear in source, config committed to VCS, or logs | M | I, T |
| NFR-16 | Redaction (`FR-PARSE-3`) shall be verified by a test corpus of planted secrets asserting zero leakage into any store | M | T |
| NFR-17 | The system shall hold read-only credentials to monitored systems (`CON-2`) | M | I |
| NFR-18 | Dependencies shall be pinned (`CON-8`) and scanned for known vulnerabilities in CI | S | T |
| NFR-19 | Passwords shall be stored using a memory-hard KDF (argon2id or bcrypt); plain or fast-hashed storage shall be prohibited | M | I, T |
| NFR-20 | Audit logging per `FR-API-8` shall be tamper-evident (append-only) | C | I |

### 8.4 Maintainability and portability

| ID | Requirement | Pri | V |
|---|---|---|---|
| NFR-21 | Unit-test line coverage of `cg/` shall be ≥ 70%, with ≥ 90% on `cg/eval/` and `cg/calibrate/`. *Rationale:* a bug in the evaluation or calibration code silently corrupts every reported number, so those modules carry the higher bar | M | T |
| NFR-22 | CI shall run lint, type-check (mypy), unit tests and the leakage-audit tests on every push | M | T |
| NFR-23 | Public functions shall carry type hints and docstrings | S | I |
| NFR-24 | Modules shall be independently runnable: parsing, featurization, training, evaluation and serving each invocable standalone, so a rung can be dropped without breaking the harness | M | I |
| NFR-25 | The full stack shall start from a clean checkout with one documented command (`CON-10`) | M | D |
| NFR-26 | Configuration shall be file-based and environment-overridable; no behavioural constant shall be hard-coded in application code | S | I |

### 8.5 Usability

| ID | Requirement | Pri | V |
|---|---|---|---|
| NFR-27 | An operator shall be able to determine, from the incident view alone and within 60 s, what is failing, where, when it will fail, and what evidence supports that. This shall be validated by timed walkthrough with ≥ 3 test users | M | D |
| NFR-28 | Charts shall meet WCAG 2.1 AA contrast and be legible in light and dark themes | S | I |
| NFR-29 | Every model-produced number in the UI shall be traceable to its inputs via the evidence bundle | M | D |
| NFR-30 | Error messages shall state what failed and what to do next; bare stack traces shall not be surfaced to users | S | I |

---

## 9. Verification and acceptance

### 9.1 Verification methods

| Method | Applied to | Evidence produced |
|---|---|---|
| `T` Test | Functional behaviour, latency, leakage, redaction | Automated suite in CI; pass/fail + measured values |
| `A` Analysis | All §6 metrics | MLflow run + generated table/figure in `reports/` |
| `D` Demonstration | UI, testbed, end-to-end flow | Recorded walkthrough + live demo |
| `I` Inspection | Constraints, architecture, security posture | Reviewer checklist against the requirement text |

### 9.2 Acceptance criteria

The system is accepted when **all** hold:

1. Every `M`-priority requirement is verified by its stated method, with evidence recorded.
2. `run_all.sh` reproduces every table and figure in the report from a clean checkout (`FR-EXP-3`).
3. The leakage audit (`EV-12`) passes, including the `DR-5`/`DR-6`/`DR-10` tests.
4. The baseline ladder table is complete for all `M` rungs, including rung 2 (`MR-11`, `MR-12`).
5. The lead-time result is demonstrated live: an injected fault produces an alert with lead time
   ≥ δ, and the measured lead time is displayed against the actual onset.
6. The alerts-per-host-day figure is produced for both CloudGuardian and the 3σ baseline.
7. Explanation precision@3 is measured against injected ground truth with a random baseline for
   contrast (`EV-7`).
8. The point-adjustment figure (`EV-8`) is present, showing the random scorer's inflated score.
9. No unauthenticated endpoint exposes telemetry or log content (`NFR-13`), verified by test.
10. The redaction corpus test reports zero leakage (`NFR-16`).
11. Any missed §6.1 target is documented with analysis of why.

### 9.3 Acceptance demonstration script

The `D`-method evidence for criteria 5–6, to be executed live:

| Step | Action | Expected observable |
|---|---|---|
| 1 | Dashboard open, live traffic, fleet green | All hosts low risk; model health "calibrated" |
| 2 | `./chaos inject memory-leak --target worker-1 --ramp 6m` | Injector writes the ground-truth episode |
| 3 | ~T+90 s | Risk rises (≈0.08 → 0.34); **no alert** — narrate that the FDR gate is correctly withholding on insufficient evidence (`FR-CAL-3`) |
| 4 | ~T+3 min | Alert raised; TTF panel shows p50/p90 band |
| 5 | Click the incident | Evidence bundle: top metrics with SHAP and baselines, top templates with window vs. baseline counts, computed counterfactual, similar incident + resolution |
| 6 | ~T+9 min | Worker OOMs; overlay alert timestamp on onset |
| 7 | Read the measured lead time | ≥ δ, and ≥ 4 min per §6.1 |
| 8 | Open the evaluation view | 3σ baseline alerts/host-day vs. CloudGuardian's, at equal recall |

---

## 10. Traceability

### 10.1 Objectives → requirements

| Objective | Satisfied by |
|---|---|
| **OBJ-1** AI-based predictive maintenance system | MR-1…MR-12, FR-INF-1…7, FR-EXP-1…6 |
| **OBJ-2** Process structured metrics **and** unstructured logs | FR-ING-1, FR-ING-2, FR-PARSE-1…8, FR-FEAT-2, FR-FEAT-3, FR-FEAT-4, MR-4, MR-8…MR-10 |
| **OBJ-3** Predict failures before they occur | MR-1 (heads 3–4), FR-INF-1, FR-INF-3, DR-5, DR-6, DR-9, EV-3, EV-4, EV-5, FR-TB-3 |
| **OBJ-4** Explainable root cause analysis | FR-XAI-1…15, EV-7, FR-UI-3, NFR-29 |
| **OBJ-5** Real-time dashboard, visualization, alerts | FR-API-1…8, FR-UI-1…10, FR-ALERT-1…5, NFR-3, NFR-8 |

### 10.2 Stated problems → requirements

The five limitations in the problem statement, each mapped to the requirements that address it.
This table is the argument that the specification is complete with respect to the brief.

| # | Stated limitation of current systems | Addressed by | How |
|---|---|---|---|
| 1 | Relies on predefined thresholds | FR-CAL-1, FR-CAL-2, FR-CAL-5, MR-11 rung 1 | Learned models + conformal p-values replace thresholds; the 3σ system is retained as the measured baseline so the improvement is quantified rather than asserted |
| 2 | Cannot understand context of textual logs | FR-PARSE-1…6, FR-FEAT-2, MR-4, MR-8…10 | Templates + cached semantic embeddings + cross-attention fusion; three simultaneous representation views; unseen templates handled by embedding neighbour rather than discarded |
| 3 | High number of false alarms | FR-CAL-2, FR-CAL-3, FR-CAL-4, FR-CAL-5, FR-DRIFT-2, EV-3(c) | Online FDR control, k-of-m hysteresis, per-host cooldown, new-template-≠-anomaly separation, and alerts-per-host-day as a first-class reported metric |
| 4 | Cannot explain root cause | FR-XAI-1…15, EV-7 | Three grounded layers; counterfactuals computed by re-running the model; every narrative claim must cite evidence; explanation quality measured against injected ground truth |
| 5 | Detects failures only after they occur | MR-1 heads 3–4, FR-INF-3, DR-5, DR-9, EV-3(a,b), EV-4, FR-TB-3 | Horizon-based risk + hazard TTF head; leakage rules that make lead time real; lead-time distribution as the headline metric; δ-gated so a late alert cannot be reported as a prediction |

### 10.3 Requirement counts

Generated from the requirement tables; regenerate when requirements change.

| Section | M | S | C | Total |
|---|---|---|---|---|
| §3 Data (incl. DR-1.x sources) | 14 | 4 | 2 | 20 |
| §4 Functional | 71 | 25 | 3 | 99 |
| §5 Model | 11 | 1 | 0 | 12 |
| §6 Evaluation | 11 | 1 | 0 | 12 |
| §7 Interfaces | 3 | 1 | 0 | 4 |
| §8 Non-functional | 19 | 10 | 1 | 30 |
| **Total** | **129** | **42** | **6** | **177** |

Plus 5 objectives, 10 constraints, 8 assumptions and 5 open questions, all cross-referenced and
verified to resolve (no dangling references).

---

## 11. Appendices

### 11.1 Appendix A — default configuration values

| Parameter | Symbol | Default | Requirement |
|---|---|---|---|
| Tick interval | Δ | 30 s | FR-ING-3 |
| Window length | L | 60 ticks (30 min) | FR-FEAT-1 |
| Prediction horizons | H | {2.5, 5, 10, 20} min | FR-INF-3 |
| Minimum actionable lead | δ | 120 s | DR-9 |
| Target FDR | α | 0.05 | FR-CAL-2 |
| Hysteresis | k-of-m | 3 of 5 | FR-CAL-3 |
| Alert cooldown | — | 600 s | FR-CAL-4 |
| Counterfactual baseline | — | 7-day per-channel median | FR-XAI-4 |
| Sequence view length | S | 128 templates | FR-FEAT-2 |
| Template embedding dim | d_emb | 384 (MiniLM class) | MR-8 |
| Model hidden dim | d | 128 | MR-3 |
| TCN dilations | — | {1,2,4,8,16} | MR-3 |
| Seeds per experiment | — | 5 | FR-EXP-4 |
| Default retention | — | windows 7 d / scores 90 d / incidents ∞ | DR-15 |

### 11.2 Appendix B — evidence bundle schema (`FR-XAI-11`)

The complete input to narrative generation and the payload behind the incident view. The LLM sees
this and nothing else.

```json
{
  "window":   {"host": "db-02", "t": "2026-07-30T14:22:00Z", "risk": 0.71, "p_value": 0.004},
  "ttf_estimate_min": {"p50": 7, "p90": 19},
  "top_metrics": [
    {"id": "m1", "name": "pg_pool_wait_p99", "shap": 0.31,
     "value": "412ms", "baseline_p50": "18ms"},
    {"id": "m2", "name": "mem_rss_slope",    "shap": 0.22,
     "value": "+8.1MB/min", "baseline_p50": "+0.1MB/min"}
  ],
  "top_templates": [
    {"id": 47, "text": "pool timeout acquiring connection after <*> ms",
     "count_window": 214, "count_baseline": 0, "surprise": 9.2,
     "example": "pool timeout acquiring connection after 5000 ms"}
  ],
  "counterfactual": [
    {"channel": "pg_pool_wait_p99", "to": "baseline_p50",
     "risk_before": 0.71, "risk_after": 0.14}
  ],
  "similar_incidents": [
    {"id": "INC-118", "similarity": 0.89, "resolution": "pool size 20 -> 60"}
  ],
  "runbook_chunks": ["..."],
  "new_templates_this_window": 0,
  "model": {"version": "cg-0.4.1", "feature_spec": "fs-3", "calibration": "calibrated"}
}
```

Validation rules: schema-valid or rejected; every sentence in the generated narrative must cite at
least one `id` from `top_metrics` or `top_templates`; uncited output is rejected; if
`top_metrics` and `top_templates` are both empty, the brief must be `insufficient_evidence`.

### 11.3 Appendix C — leakage audit checklist (`EV-12`)

| Check | Requirement | Test |
|---|---|---|
| No risk-head label derived from inside [onset, recovery] | DR-5 | Assert masked ticks absent from the training index |
| Precursor windows absent from the "normal" AE training set | DR-6 | Assert set intersection is empty |
| Splits are chronological and non-overlapping | DR-7 | Assert max(train.ts) < min(cal.ts) < min(test.ts) |
| Calibration split is anomaly-free | DR-8 | Assert label sum == 0 |
| Lead time ∈ [δ, H] enforced for TP credit | DR-9 | Unit test on synthetic alert/onset pairs |
| No future data in features at tick t | DR-10 | Feed future-shifted input; assert output invariance |
| Normalisation fitted on train only | DR-10 | Assert scaler state hash unchanged by test data |
| Resampling confined to the training split | DR-13 | Assert no synthetic id appears in cal/test |
| Data hash recorded per run | DR-11 | Assert artefact contains hash, git SHA, seed |

### 11.4 Appendix D — known risks

| Risk | Affects | Mitigation |
|---|---|---|
| BGL lead-time labels noisy | EV-3 | DR-12: ≥ 2 label constructions, sensitivity reported |
| Testbed faults too easy → 100% detection, meaningless | EV-3, FR-TB | Slow precursor ramps, background load noise, precursor-strength sweep (FR-TB-6) |
| Too few positives to train risk head | MR-1, MR-6 | Masked multi-task loss (MR-2) lets unlabelled data train heads 1–2; many short episodes rather than few long ones |
| Sentence-encoder cost breaks CPU latency | NFR-1 | Template cache (FR-PARSE-5), MiniLM, ONNX quantisation; measured in EV-9 |
| Drift invalidates conformal guarantee | FR-CAL-1 | FR-DRIFT-1…3 recalibration; explicit "degraded"/"uncalibrated" UI state |
| Cross-attention fusion no better than late fusion | MR-4, MR-5 | Pre-committed ablation (MR-5); reporting the negative result is an accepted outcome |
| Scope overrun | all | Priority ladder; §4.12 harness + `M` rungs are the defensible core and are scheduled first |

### 11.5 Appendix E — revision history

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-07-30 | — | Initial specification. Baselined against CG-PLAN-001 (R20) |

### 11.6 Appendix F — open questions

| # | Question | Blocks | Needed by |
|---|---|---|---|
| Q1 | Kafka or Redis Streams for the transport profile? Redis is materially simpler to operate; Kafka is more defensible as "production-shaped" | FR-ING-2 | Before ingestion work starts |
| Q2 | TimescaleDB or ClickHouse? | FR-STORE-1 | Before storage work starts |
| Q3 | Is Exathlon acquisition feasible within schedule? If not, `EV-7` rests on the testbed alone and the report must say so | DR-1.4, EV-7 | Before the explanation-evaluation work |
| Q4 | Confirm δ = 120 s is operationally meaningful for the fault classes in scope | DR-9 | Before lead-time evaluation |
| Q5 | Are narrative briefs in the assessed scope, or a stretch demo? | FR-XAI-10…15 | Before the narrative work |

---

*End of document — CG-SRS-001 v1.0*

