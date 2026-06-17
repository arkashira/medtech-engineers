# TECH_SPEC.md

## 1. Overview

`medtech-engineers` is a SaaS platform that matches medical‑device and health‑tech startups with pre‑trained, full‑stack software engineers.  
The platform exposes a **matchmaking API** that:

1. Accepts a *project brief* (domain, tech stack, regulatory constraints, timeline, budget).  
2. Returns a ranked list of candidate engineers with skill scores, availability, and cost estimates.  
3. Supports real‑time updates, notifications, and contract management.

The system is built for **high availability**, **data privacy** (HIPAA‑like compliance), and **scalable matchmaking**.

---

## 2. Architecture Overview

```
┌───────────────────────┐
│  Client (Web / Mobile)│
└─────────────┬─────────┘
              │ REST/GraphQL
┌─────────────▼─────────┐
│  API Gateway (NGINX)  │
└─────────────┬─────────┘
              │
┌─────────────▼─────────┐
│  Auth Service (Keycloak) │
└─────────────┬─────────┘
              │
┌─────────────▼─────────┐
│  Matchmaking Service   │
│  (Node.js / TypeScript)│
└───────┬───────┬───────┘
        │       │
┌───────▼───────▼───────┐
│  Skill‑Score Engine   │
│  (Python / FastAPI)   │
└───────┬───────┬───────┘
        │       │
┌───────▼───────▼───────┐
│  Data Store (PostgreSQL) │
└───────┬───────┬───────┘
        │       │
┌───────▼───────▼───────┐
│  Vector Store (pgvector) │
└───────┬───────┬───────┘
        │       │
┌───────▼───────▼───────┐
│  Notification Service (Kafka + Redis) │
└───────┬───────┬───────┘
        │       │
┌───────▼───────▼───────┐
│  Billing & Contracts (Stripe, DocuSign) │
└───────────────────────┘
```

* **API Gateway**: TLS termination, rate limiting, CORS.  
* **Auth Service**: OAuth2 / OpenID Connect, role‑based access control.  
* **Matchmaking Service**: Orchestrates candidate retrieval, ranking, and contract creation.  
* **Skill‑Score Engine**: Computes skill vectors from CVs, GitHub, and interview data; stores them in `pgvector`.  
* **Data Store**: Relational schema for users, projects, contracts, logs.  
* **Vector Store**: Stores high‑dimensional embeddings for fast similarity search.  
* **Notification Service**: Push (WebSocket), email, SMS.  
* **Billing**: Stripe for subscription, DocuSign for e‑signature.

---

## 3. Components & Interfaces

| Component | Responsibility | Key APIs | Tech |
|-----------|----------------|----------|------|
| **Auth Service** | User registration, login, token issuance | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` | Keycloak, OpenID Connect |
| **Project Service** | CRUD for project briefs | `POST /projects`, `GET /projects/{id}`, `PUT /projects/{id}`, `DELETE /projects/{id}` | Express.js |
| **Engine Service** | Matchmaking logic, ranking | `POST /match`, `GET /match/{id}` | Node.js, TypeScript |
| **Skill Engine** | Compute & update skill vectors | `POST /skills/update`, `GET /skills/{engineerId}` | FastAPI, Python |
| **Vector Store** | Similarity search | `POST /vector/search` | pgvector |
| **Notification Service** | Real‑time alerts | `POST /notify`, WebSocket `/ws/notifications` | Kafka, Redis |
| **Billing Service** | Subscription, invoicing | `POST /billing/subscribe`, `GET /billing/invoices` | Stripe API |
| **Contract Service** | e‑signature, storage | `POST /contracts`, `GET /contracts/{id}` | DocuSign API |

All services expose **OpenAPI 3.0** definitions for auto‑generation of SDKs.

---

## 4. Data Model

### 4.1 Relational Schema (PostgreSQL)

```sql
-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('client', 'engineer', 'admin')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Projects
CREATE TABLE projects (
  id UUID PRIMARY KEY,
  client_id UUID REFERENCES users(id),
  title TEXT NOT NULL,
  description TEXT,
  tech_stack TEXT[],
  regulatory_requirements TEXT[],
  timeline_days INT,
  budget_cents INT,
  status TEXT NOT NULL DEFAULT 'open',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Engineers
CREATE TABLE engineers (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  bio TEXT,
  location TEXT,
  availability_days INT,
  hourly_rate_cents INT,
  skills JSONB,          -- e.g., {"embedded": 5, "firmware": 4}
  vector VECTOR(512),    -- pgvector embedding
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Contracts
CREATE TABLE contracts (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  engineer_id UUID REFERENCES engineers(id),
  signed_at TIMESTAMP WITH TIME ZONE,
  status TEXT NOT NULL CHECK (status IN ('draft', 'signed', 'cancelled')),
  amount_cents INT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

### 4.2 Vector Store (pgvector)

* **Engineers**: 512‑dimensional embedding derived from CV, GitHub repos, and interview transcripts.  
* **Projects**: 512‑dimensional embedding of project brief (text + tags).  
Similarity is computed with `cosine_distance`.

---

## 5. Key Algorithms

### 5.1 Skill‑Vector Generation

1. **Text Extraction**: Parse CV, README, GitHub commit messages.  
2. **Embedding**: Use OpenAI GPT‑4 embedding (`text-embedding-3-large`) → 1536‑dim vector.  
3. **Dimensionality Reduction**: PCA to 512 dimensions.  
4. **Normalization**: L2‑normalize.  
5. **Storage**: Insert into `engineers.vector`.

### 5.2 Matchmaking Ranking

For a given project:

1. Retrieve project vector.  
2. Compute cosine similarity with all engineer vectors.  
3. Apply **skill‑match score**: weighted sum of skill levels vs required tech stack.  
4. Apply **availability & budget filters**.  
5. Rank by composite score:  
   `score = 0.5 * similarity + 0.3 * skill_match + 0.2 * availability_score`.

---

## 6. Tech Stack

| Layer | Technology | Reason |
|-------|------------|--------|
| **API Gateway** | NGINX + Lua | TLS, rate limiting |
| **Auth** | Keycloak | OpenID Connect, SSO |
| **Backend** | Node.js 20, TypeScript | Fast development, async I/O |
| **Skill Engine** | Python 3.12, FastAPI | ML inference, vector ops |
| **Database** | PostgreSQL 15 + pgvector | ACID, vector search |
| **Message Bus** | Kafka 3.x | Decoupled notifications |
| **Cache** | Redis 7 | Session, pub/sub |
| **Billing** | Stripe, DocuSign | Subscription, e‑signature |
| **Containerization** | Docker, Docker‑Compose | Reproducible builds |
| **CI/CD** | GitHub Actions | Automated tests, lint, deploy |
| **Infrastructure** | Terraform + AWS (EKS) | IaC, autoscaling |
| **Observability** | Prometheus + Grafana, Loki | Metrics, logs |
| **Security** | OWASP Top 10, Snyk | Vulnerability scanning |

---

## 7. Deployment

### 7.1 Local Development

```bash
# Clone repo
git clone https://github.com/axentx/medtech-engineers.git
cd medtech-engineers

# Start services
docker compose up --build

# Run tests
npm run test
```

### 7.2 Production

1. **Infrastructure**: Terraform applies to AWS EKS cluster.  
2. **CI/CD**: GitHub Actions builds Docker images, pushes to ECR, applies Helm charts.  
3. **Secrets**: Managed via AWS Secrets Manager (Keycloak credentials, Stripe keys).  
4. **Scaling**: Horizontal Pod Autoscaler on CPU/memory; Kafka partitions for high throughput.  
5. **Backup**: Daily PostgreSQL dumps to S3, pgvector snapshots.  
6. **Monitoring**: Prometheus alerts for latency > 200ms, error rate > 1%.

---

## 8. Security & Compliance

| Requirement | Implementation |
|-------------|----------------|
| **Data Encryption** | TLS 1.3 for all traffic; AES‑256‑GCM at rest (PostgreSQL). |
| **Access Control** | RBAC via Keycloak; fine‑grained scopes. |
| **Audit Logging** | All API calls logged to Loki; immutable audit trail. |
| **HIPAA‑like** | Data segregation per tenant; encryption keys rotated quarterly. |
| **GDPR** | Right to delete, data export endpoints. |

---

## 9. Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| `express` | ^4.18.2 | HTTP server |
| `typeorm` | ^0.3.12 | ORM for PostgreSQL |
| `pgvector` | ^0.1.0 | Vector extension |
| `fastapi` | ^0.95.0 | Skill engine |
| `pydantic` | ^1.10.2 | Data validation |
| `openai` | ^3.0.0 | Embedding API |
| `kafka-node` | ^6.0.0 | Messaging |
| `stripe` | ^11.0.0 | Billing |
| `docusign-esign` | ^3.0.0 | e‑signature |
| `redis` | ^4.0.0 | Cache & pub/sub |

---

## 10. Future Enhancements

1. **AI‑Driven Interview Assistant** – automated skill assessment.  
2. **Dynamic Pricing Engine** – real‑time cost estimation based on market demand.  
3. **Marketplace Analytics Dashboard** – insights for clients and engineers.  
4. **Multi‑tenant Data Isolation** – stricter schema separation for compliance.

---

*Prepared by: Senior Product/Engineering Lead – Axentx*
