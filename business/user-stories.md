Generated `user-stories.md` — 12 stories across 4 epics for **medtech-engineers**.

**Epics & coverage:**
- **Talent Matching** (3) — skill-scoped search, evidence-backed vetting, fit-scored ranking. *This is the product; addresses the core buyer fear of generalist contractors.*
- **Compliance-Ready Engagements** (3) — IEC 62304/ISO 13485/HIPAA filtering, audit-ready starter kits, BAA-covered workspaces. *The moat vs. Toptal/Upwork.*
- **Delivery Operations** (3) — paid trial-to-contract, escrowed milestones, engagement-health dashboard. *Drives retention/unit economics.*
- **Talent Supply** (3) — assessment pipeline, availability/rate management, workspace handoff. *Solves the marketplace cold-start.*

Complexity mix: **2 S / 7 M / 3 L**. Each story has 3–4 acceptance criteria with numeric targets where it matters (e.g. <800ms search, top-5 in 60s, 15-min provisioning).

Opinionated calls baked in:
- **MVP cut** named explicitly (US-1.1, 1.2, 2.1, 3.1, 4.1) to prove the match→vet→trial→supply loop before building escrow/compliance scaffolding.
- Cross-references between stories (US-4.3 reuses US-2.2's starter kit) to signal the integration seams.
- Compliance tags are **evidence-gated, not self-asserted** — the single most important differentiator for a regulated-industry talent platform.