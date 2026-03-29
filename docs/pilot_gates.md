# Staging-Checkliste — Pilot-Gate A / Pilot-Gate B

Kompakt, eindeutig, ohne Diskussion interpretierbar.  
Technische Details: [`ghost_staging_e2e.md`](ghost_staging_e2e.md), [`security_production.md`](security_production.md), [`Deployment.md`](Deployment.md).

---

## Gate A — Security & Hygiene (muss grün sein)

**Ziel:** „System ist sicher genug für einen Pilot.“

- [ ] **Gitleaks (GitHub Actions):** letzter Run auf `master` **grün** — [`.github/workflows/gitleaks.yml`](../.github/workflows/gitleaks.yml)
- [ ] **Gitleaks lokal:** `gitleaks detect --source . --config .gitleaks.toml` → **`no leaks found`**
- [ ] **Keine Secrets im Repo** (ENV, Keys, Tokens) — nur Platzhalter / Secret-Store
- [ ] **Alembic-Migrations** statt `create_all` in Staging/Prod — siehe [`Deployment.md`](Deployment.md)
- [ ] **TLS** in Staging **aktiviert** (HTTPS zur API)
- [ ] **Auth aktiv** (API-Key oder Token wie von euch ausgegeben)
- [ ] **Rate-Limits / Budgets** gesetzt, **falls** im Pilot-Scope vorgesehen — siehe [`security_production.md`](security_production.md)

**Gate A erfüllt:** alle Checkboxen erledigt.

---

## Gate B — Nutzbarkeit / E2E-Flow (muss durchlaufen)

**Ziel:** „Ein Nutzer kann Arctis Ghost ohne Hilfe nutzen.“

### Voraussetzungen

- API erreichbar — **GET `/health`** grün (Arctis-Standard; nicht `/healthz`)
- Tenant existiert
- API-Key gesetzt (z. B. `ARCTIS_API_KEY`)
- `workflow_id` in `ghost.yaml` gesetzt (nach `init-demo` Platzhalter ersetzen)
- **Gleiche Umgebung** wie später „lokal“ / Staging

### E2E-Flow (ohne Repo-Hilfe)

- [ ] `ghost init-demo`
- [ ] `ghost doctor`
- [ ] `ghost run input.json` (oder anderes Execute-Body-JSON im Arbeitsverzeichnis — konsistent mit [`ghost_cli_reference.md`](ghost_cli_reference.md))
- [ ] `ghost pull-artifacts <run_id>`
- [ ] `ghost verify <run_id>`

(`<run_id>` = Ausgabe von `ghost run`.)

**Gate B erfüllt:** alle fünf Schritte **ohne Fehler**.

---

## Interpretation (Team, Support, Audit, Sales)

| | |
|--|--|
| **Gate A** | „**Dürfen** wir starten?“ (Security & Hygiene) |
| **Gate B** | „**Funktioniert** es für Nutzer?“ (Nutzbarkeit) |

- **A grün + B grün** → **Pilot-ready**
- **A rot** → **kein Pilot**
- **B rot** → **kein Pilot**
- **A grün + B rot** → **Produkt-/Ops-Problem**, kein Security-Freifahrtschein — Ghost/API/Doku/Umgebung nachziehen

Diese Trennung ist intern wie extern nützlich.

---

## Nachweis (Staging-E2E-Dokument)

Nach erstem erfolgreichen Durchlauf: Status in [`ghost_staging_e2e.md`](ghost_staging_e2e.md) aktualisieren (Datum, Umgebungsname, keine Secrets).
