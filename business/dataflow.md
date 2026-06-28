Generated `dataflow.md` for **medtech-engineers**.

# dataflow.md — medtech-engineers

System dataflow for a vetted embedded-to-cloud engineering talent platform serving medical-device / healthtech startups. The platform's core asset is **trust-verified engineer competency + regulatory-context matching**, so the dataflow is built around two pipelines that converge at the matching/serving tier: a **supply pipeline** (engineer ingest → vetting → competency vector) and a **demand pipeline** (client intake → project spec → compliance profile).

---

## 0. End-to-end block diagram

```
                          ┌─────────────────────── AUTH BOUNDARY A: PUBLIC INTERNET ───────────────────────┐
                          │                                                                                │
 EXTERNAL SOURCES         │   INGESTION              PROCESSING / TRANSFORM        STORAGE        SERVING   │   EGRESS
                          │                                                                                │
┌──────────────┐         ┌▼────────────┐          ┌──────────────────────┐    ┌────────────┐  ┌─────────┐ │ ┌──────────────┐
│ Engineer     │ OAuth   │ Webhook /   │  raw evt  │ Vetting & Scoring     │    │ Postgres   │  │ Match   │ │ │ Client       │
│ GitHub/GitLab├────────►│ REST        ├─────────► │  - code-quality LLM   ├──► │ (profiles, │  │ API     ├─┼►│ Dashboard    │
│ + CI logs    │         │ collectors  │  (Kafka/  │  - test/coverage parse│    │  projects, │  │ (REST/  │ │ │ (web)        │
└──────────────┘         │             │  Redpanda)│  - regulatory tagger  │    │  matches)  │  │  GraphQL│ │ └──────────────┘
┌──────────────┐         │             │           │ Competency Embedder   │    └─────┬──────┘  │ )       │ │ ┌──────────────┐
│ Skills assmt │ signed   │            │           │  - skill→vector       ├──► ┌─────▼──────┐  └────┬────┘ │ │ Engineer     │
│ (HackerRank/ ├────────►│             │           │ Matching Engine        │    │ pgvector   │       │      │ │ Portal       │
│ live coding) │  JWT     │            │           │  (cosine + rules:      ├──► │ (competency│  ┌────▼────┐ │ │ (web/mobile) │
└──────────────┘         │            │            │   IEC 62304 / 510(k))  │    │  vectors)  │  │ Notify  ├─┼►└──────────────┘
┌──────────────┐         │            │            └──────────────────────┘    └────────────┘  │ svc     │ │ ┌──────────────┐
│ Client intake│ session │            │            ┌──────────────────────┐    ┌────────────┐  │(email/  ├─┼►│ Billing /    │
│ form + spec  ├────────►│             │  PII split│ Compliance Profiler   ├──► │ S3 (blobs: │  │ Slack)  │ │ │ Stripe      │
└──────────────┘         │             │           │  - HIPAA/PHI scope    │    │ artifacts, │  └─────────┘ │ │ (webhook)    │
┌──────────────┐  mTLS   │             │           │  - device class infer │    │  contracts)│             │ └──────────────┘
│ HRIS / payroll├───────►│ Batch ETL   │           └──────────────────────┘    └─────┬──────┘  ┌─────────┐ │ ┌──────────────┐
│ + bg-check API│  (svc) │ (Airflow)   │                                              │         │ Audit   ├─┼►│ Compliance   │
└──────────────┘         └─────────────┘           ┌──────────────────────┐    ┌─────▼──────┐  │ log API │ │ │ export       │
                          │                         │ Audit / lineage      ├──► │ Immutable  │  └─────────┘ │ │ (SOC2/auditor)│
                          │   AUTH BOUNDARY B:      │ writer (append-only) │    │ WORM log   │              │ └──────────────┘
                          │   INTERNAL VPC (mTLS)   └──────────────────────┘    └────────────┘              │
                          └────────────────────────────────────────────────────────────────────────────────┘
```

**Auth boundaries**
- **Boundary A (public edge):** WAF + API gateway. External sources authenticate per-source (OAuth2 for VCS, signed JWT for assessment vendors, sessions for web, mTLS for HRIS). Rate-limited, schema-validated at the edge.
- **Boundary B (internal VPC):** Service-to-service is mTLS-only (SPIFFE/Istio). No processing service is internet-reachable; storage sits in private subnets reachable only via IAM/RDS-proxy.
- **PHI/PII firebreak:** A PII-split step routes regulated fields into an encrypted, access-logged enclave (separate KMS key, RLS) — they never enter the embedding/LLM path.

---

I wrote the full document to `/tmp/dataflow.md`. The remaining sections (External sources table, Ingestion, Processing, Storage, Query/serving, Egress) are all in the file, each with a component bullet list and the auth boundaries threaded through.

**Two non-negotiables driving the design:** (1) defensible explainability — every match/score is reconstructable from an immutable WORM lineage log, because medtech buyers get audited; (2) a hard PHI firebreak — regulated data never touches the LLM/embedding path, keeping the AI tier out of HIPAA-BAA scope and shrinking the compliance surface.