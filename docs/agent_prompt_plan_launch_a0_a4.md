<!--
  Source of Truth: Launch-Orchestrierung für Arctis (Agent + Mensch).
  Normative Produkt-/Engine-Spec bleibt: docs/pipeline-a-v1.3.md
-->
# Agent Prompt Plan — Arctis Launch (A0 → A4)

**Version:** 1.0.0 — ausgerichtet auf Arctis **v0.1.0** ([`pyproject.toml`](../pyproject.toml), [`CHANGELOG.md`](../CHANGELOG.md))  
**Status:** operationalisierbarer Launch-Orchestrator (Phasen, Gates, Artefakte, Owner, Policies)

Dieses Dokument ist die **Single Source of Truth** für **Betrieb, Doku, Packaging und Launch-Gates** — nicht für Pipeline-/IR-/Engine-Verhalten.

---

## Inhalt

| Abschnitt | Beschreibung |
|-----------|----------------|
| [Globale Regeln](#globale-regeln-für-jede-session) | Scope, Secrets, Verifikation |
| [Commit-Policy](#commit-policy) | Wann committen, was verboten ist |
| [Stop-Condition](#stop-condition) | Wann der Agent stoppt |
| [Phase-Switch-Policy](#phase-switch-policy--scorecard) | Kein A1 vor abgeschlossenem A0 |
| [Owner & Review](#owner--review) | Verantwortlichkeiten |
| [Master-Prompt](#master-prompt-session-start) | Copy-Paste für Agent-Sessions |
| [Phasen A0–A4](#phase-a0--zero-interface--ghost--doku) | Aufgaben, Gates, Links |
| [Anti-Patterns](#-anti-patterns) | Vermeiden |
| [Optional: CI](#optional-ci-integration-später-a1a2) | Spätere Automatisierung |
| [Session-Ende](#session-start--ende) | Trigger & Stopp |

### Wichtige Repo-Querverweise

| Thema | Datei |
|--------|--------|
| Ghost CLI (vollständig) | [`docs/ghost_cli_reference.md`](ghost_cli_reference.md) |
| Ghost Quickstart (anlegen/pflegen in A0.1) | [`docs/ghost_quickstart.md`](ghost_quickstart.md) |
| 60s-Demo | [`docs/arctis_ghost_demo_60.md`](arctis_ghost_demo_60.md) |
| Demo-Matrix | [`docs/demo_matrix.md`](demo_matrix.md) |
| Deployment | [`docs/Deployment.md`](Deployment.md) |
| Security Production | [`docs/security_production.md`](security_production.md) |
| DR | [`docs/DR.md`](DR.md) |
| Release & Tags | [`docs/RELEASE.md`](RELEASE.md) |
| Staging E2E (G4) | [`docs/ghost_staging_e2e.md`](ghost_staging_e2e.md) |
| Pilot-Gate A/B (Checklisten) | [`docs/pilot_gates.md`](pilot_gates.md) |
| Package / Wheel-Strategie | [`docs/arctis_package_strategy.md`](arctis_package_strategy.md) |
| Launch-Checkliste (Prod) | [`DEPLOYMENT_CHECKLIST.md`](../DEPLOYMENT_CHECKLIST.md) |
| Launch-Skript | [`arctis/scripts/launch_check.py`](../arctis/scripts/launch_check.py) |
| Gitleaks | [`.gitleaks.toml`](../.gitleaks.toml), [`.gitleaksignore`](../.gitleaksignore) |
| CI | [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) |
| Mitwirkung | [`CONTRIBUTING.md`](../CONTRIBUTING.md) |

---

## Globale Regeln (für jede Session)

1. **Kontext laden:** Siehe Tabelle oben; mindestens [`README.md`](../README.md) + die für die Teilaufgabe genannten Dateien.
2. **Keine Secrets:** Niemals API-Keys, Tokens oder Klartext-Credentials committen. Platzhalter: `<REDACTED>` oder nur **Namen** von Umgebungsvariablen (`ARCTIS_API_KEY`, …). [`.gitleaks.toml`](../.gitleaks.toml) respektieren.
3. **Scope:** Nur Dateien ändern, die die **aktuelle Teilaufgabe** braucht — keine Drive-by-Refactors.
4. **Verifikation:** Abschluss nur mit **konkretem Check** (Exit-Code, Diff-Review, Link-Konsistenz).
5. **Windows/Linux:** Pfade in Doku mit `/`; Ghost-Commands plattformunabhängig halten.
6. **Eine Kanonik:** Nach [A0.1](#a01--ordner-kanonik-festlegen) gibt es **genau eine** dokumentierte Ordner-/Workflow-Wahrheit (kein stiller Drift zwischen README, `init-demo`, Harness-[`input/`](../input/README.md)).

---

## Commit-Policy

> **Commits** nur auf **explizite Freigabe** durch den Menschen (z. B. „Commit ausführen“, „merge“).  
> **Keine Secrets** im Diff. **Keine** unnötigen Refactors außerhalb der Teilaufgabe.  
> Kleine, reviewbare Commits pro logischer Einheit bevorzugen.

---

## Stop-Condition

> **Stopp:** Sobald die **Teilaufgabe** (z. B. A0.2) erfüllt ist: **anhalten**, Report liefern, auf **Freigabe für Commit** oder nächste Teilaufgabe warten — nicht „mit A0.3 weitermachen“, es sei denn, der Nutzer weist es an.

---

## Phase-Switch-Policy & Scorecard

**Regel:** Keine neue **Phase** (z. B. A1) starten, bevor die vorherige **Phase** abgeschlossen ist und die Scorecard **voll** ist.

### Scorecard (am Ende jeder Phase ausfüllen)

| Kriterium | 0 = offen | 1 = erfüllt |
|-----------|-----------|-------------|
| Doku = ausführbar ohne Rückfragen | ☐ | ☐ |
| Keine Secret-Leaks / Gitleaks ok | ☐ | ☐ |
| Gates explizit getestet (Command / Checkbox) | ☐ | ☐ |
| Eindeutige Ordner-Kanonik (ab A0 fertig) | ☐ | ☐ |

**Schwellenwert:** Erst wenn **alle vier** Kriterien **1** sind → nächste Phase freigeben.  
Wenn ein Kriterium **0** bleibt → Phase **nicht** als „done“ markieren; Drift und Scope-Creep vermeiden.

---

## Owner & Review

| Phase | Owner | Reviewer / Stakeholder |
|-------|--------|-------------------------|
| A0 | Noah | Zweite Leseperspektive (selbst oder Peer) |
| A1 | Noah | Optional: Infra-/Security-Review |
| A2 | Noah | Testnutzer oder fremder Clone ohne Repo-Hilfe |
| A3 | Noah | Launch-Partner / Early-Access-Kontakt |
| A4 | Noah | Auswertung Telemetrie / Feedback |

---

## Master-Prompt (Session-Start)

Kopieren, `{PHASE}` und `{ID}` ersetzen (z. B. `A0`, `A0.1`), in eine neue Agent-Session einfügen:

```text
Du arbeitest im Arctis-Repository (Clone-Root).

Pflichtlektüre: docs/agent_prompt_plan_launch_a0_a4.md (globale Regeln, Commit-Policy, Stop-Condition).

Führe NUR die Phase {PHASE} / Teilaufgabe {ID} aus. Keine späteren Teilaufgaben mit erledigen.

Halte dich an: keine Secrets, kein Scope-Creep, Verifikation am Ende.

Report am Ende: (1) geänderte Dateien, (2) ausgeführte Commands mit Ergebnis, (3) offene Punkte.

Commit: nur wenn der Nutzer ausdrücklich Freigabe gibt.
```

---

# PHASE A0 — Zero-Interface / Ghost / Doku

## A0.1 — Ordner-Kanonik festlegen

**Ziel:** Eine **einzige** Wahrheit für Kunden- und Ghost-Workflows.

**Empfohlen: Option A**

- Arbeitsverzeichnis: **`input/`** (Payloads), **`output/`** (falls lokal), **`ghost.yaml`**, Artefakte unter **`outgoing/<run_id>/`** nach [`ghost pull-artifacts`](ghost_cli_reference.md).
- **Abgrenzung:** Repo-Root [`input/`](../input/README.md) / [`output/`](../output) = Harness-/Task-Inputs (nummerierte Tasks), **nicht** automatisch identisch mit dem Ghost-Demo-Ordner — das muss im README stehen.

**Option B** (nur bei Bedarf): zusätzlich `sandbox/input`, `sandbox/output`, `sandbox/evidence`, `sandbox/recipes` + `.gitkeep` + `sandbox/README.md` mit Policy „keine Secrets“.

### To-Do

- [ ] Entscheidung A oder B in [`README.md`](../README.md) (Abschnitt Verzeichnisse / Kanonik).
- [ ] [`docs/ghost_quickstart.md`](ghost_quickstart.md) anlegen oder vervollständigen (eine Seite: Kanonik + Mindest-Commands).
- [ ] Bei Option B: `sandbox/`-Struktur, `.gitkeep`, `sandbox/README.md`.

### Gate A0.1

- [ ] [`README.md`](../README.md) und [`docs/ghost_quickstart.md`](ghost_quickstart.md) widersprechen sich nicht.
- [ ] Veraltete Begriffe (`incoming/` …) bereinigt oder erklärt.

---

## A0.2 — Ghost-Demo-Flow finalisieren

**Ziel:** Doku = ausführbare Realität.

### Pflicht-Commands

```bash
ghost init-demo
ghost doctor
ghost run input.json
ghost watch <run_id>
ghost explain <run_id>
ghost pull-artifacts <run_id>
ghost verify <run_id>
```

### To-Do

- [ ] Kompletter Durchlauf (lokale oder Staging-API; `ARCTIS_API_KEY` / URL vom Menschen oder dokumentiert als Voraussetzung).
- [ ] Screenshot oder Terminal-Log unter `docs/` verlinken oder optional Ordner `docs/assets/` anlegen (ohne Secrets).
- [ ] [`docs/arctis_ghost_demo_60.md`](arctis_ghost_demo_60.md) an echte Reihenfolge anpassen.
- [ ] [`README.md`](../README.md): Abschnitt **„Try Arctis in 30 seconds“**.

### Gate A0.2

- [ ] Neuer Entwickler kann ohne Raten folgen; [`docs/ghost_cli_reference.md`](ghost_cli_reference.md) konsistent.

---

## A0.3 — Customer-Execute-Flow

**Ziel:** `ghost run body.json` → `pull-artifacts` → `verify` als Kern-Story.

### To-Do

- [ ] Beispiel `body.json` oder Verweis auf `init-demo`-[`input.json`](../arctis_ghost/init_demo.py); optional Recipe unter `docs/examples/` o. Ä.
- [ ] Quickstart-Block in [`README.md`](../README.md) mit Link zur CLI-Referenz.

### Gate A0.3

- [ ] Pfad „von Null bis verify“ als nummerierte Liste oder Mini-Diagramm in Doku.

---

## A0.4 — Branding & PLG

### To-Do

- [ ] [`README.md`](../README.md): Produktzeile, Zielgruppe, Ghost + API.
- [ ] [`docs/arctis_ghost_demo_60.md`](arctis_ghost_demo_60.md) + [`docs/demo_matrix.md`](demo_matrix.md) aktualisieren.
- [ ] „30 seconds“-Block konsistent mit A0.2.

### Gate A0.4

- [ ] Externe Leser: in **60 s** klar, **was** Arctis ist und **wie** der erste Run startet.

---

## A0.5 — Sandbox (nur Option B)

- [ ] Wenn A0.1 = **A:** kurz dokumentieren, dass kein `sandbox/` nötig ist (oder nur `init-demo`-Zielpfad).
- [ ] Wenn **B:** `sandbox/` wie spezifiziert, `.gitkeep`, README „keine Secrets“.

---

### Gate A0 (hart)

- [ ] Frischer Clone: `pip install -e ".[dev]"` → `ghost init-demo` → Run → `pull-artifacts` → `verify` → **Exit 0** (mit verfügbarer API).
- [ ] README + Demo-Docs widerspruchsfrei.
- [ ] Sandbox nur bei Option B vorhanden und beschrieben.

---

<details>
<summary><strong>PHASE A1 — Deployment, Infra, Secrets, Auth</strong> (anklicken zum Aufklappen)</summary>

**Ziel:** Staging/produktionsähnlich stabil.

**Referenzen:** [`docs/Deployment.md`](Deployment.md), [`DEPLOYMENT_CHECKLIST.md`](../DEPLOYMENT_CHECKLIST.md), [`arctis/scripts/launch_check.py`](../arctis/scripts/launch_check.py), [`docs/security_production.md`](security_production.md), [`docs/DR.md`](DR.md).

### A1.1 Infrastruktur

- [ ] `ENV=prod`, `DATABASE_URL`, `alembic upgrade head`, `ALLOWED_ORIGINS`, `ARCTIS_AUDIT_STORE` / `ARCTIS_AUDIT_JSONL_DIR` (Doku + reale Staging-Umgebung)

### A1.2 Secrets

- [ ] `ARCTIS_ENCRYPTION_KEY`, `CONTROL_PLANE_API_KEY`, Provider-Keys, `SENTRY_DSN`, optional Stripe — nur **Namen** im Repo, Werte im Secret Store

### A1.3 Auth

- [ ] Auth0 **oder** Supabase gewählt; Callbacks; JWT-Validation getestet; Tenant-Setup dokumentiert

### A1.4 Observability

- [ ] Prometheus / Grafana / Sentry / Alerts laut [`DEPLOYMENT_CHECKLIST.md`](../DEPLOYMENT_CHECKLIST.md)

### A1.5 DR & Backup

- [ ] Backup-Job, Restore-Test, [`docs/DR.md`](DR.md) aktuell

### A1.6 Launch-Gates

- [ ] Playwright Smoke, Locust (&lt;5 % Fehler), Statuspage, Support-Inbox
- [ ] `python -m arctis.scripts.launch_check` **grün** (Staging)

### Gate A1 (hart)

- [ ] `launch_check` grün
- [ ] [`DEPLOYMENT_CHECKLIST.md`](../DEPLOYMENT_CHECKLIST.md) vollständig abgehakt oder N/A mit Begründung
- [ ] Staging stabil

</details>

---

<details>
<summary><strong>PHASE A2 — Packaging & Customer Delivery</strong></summary>

### A2.1 Docker

- [ ] `docker build` mit Tag an Version ([`Dockerfile`](../Dockerfile), [`docs/Deployment.md`](Deployment.md))

### A2.2 Wheel

- [ ] `python -m build` → Wheel unter `dist/`; [`docs/arctis_package_strategy.md`](arctis_package_strategy.md) / README

### A2.3 SaaS-Modell

- [ ] Tenant, API-URL, API-Key, Limits — nur was im Produkt existiert; sonst Backlog markieren

### A2.4 Customer-Onboarding-Kit

- [ ] z. B. Ordner `docs/customer/` oder gebündeltes Doc: Quickstart, Demo, Evidence, Troubleshooting, Security-Notes

### Gate A2 (hart)

- [ ] Kunde ohne Repo-Zugriff kann starten (Docker **oder** Wheel **oder** SaaS — je nach Angebot)

</details>

---

<details>
<summary><strong>PHASE A3 — Launch (öffentlich / Early Access)</strong></summary>

- [ ] Landing, Pricing (falls nötig), Statuspage, Support, Demo-Video, Announcement
- [ ] Repo: [`CHANGELOG.md`](../CHANGELOG.md), [`docs/RELEASE.md`](RELEASE.md), Links

### Gate A3

- [ ] Nutzer können onboarden; Support & Status erreichbar; Release-Notes published

</details>

---

<details>
<summary><strong>PHASE A4 — Post-Launch</strong></summary>

- [ ] Telemetrie auswerten, Bugfixes, Roadmap 1.1.0, Customer Feedback in Issues/CHANGELOG

</details>

<details>
<summary><strong>PHASE A5 — Sustain & Evolve</strong> (Doku-Ergänzung)</summary>

Operativer Nachlauf nach Pilot/Go-Live — siehe [`docs/a5/README.md`](a5/README.md): Telemetrie, Bugfix-Rhythmus, Roadmap **1.1.0**, Feedback → Issues/CHANGELOG.

</details>

---

## Abhängigkeiten (Reihenfolge)

```text
A0.1 → A0.2 → A0.3 → A0.4 → [A0.5 wenn Option B] → Gate A0
  → A1.1–A1.6 → Gate A1
  → A2.1–A2.4 → Gate A2
  → A3 → A4 → A5 (optional, Sustain)
```

Parallel möglich: A0.4 (Copy) teilweise mit A0.2, sobald A0.1 steht.

---

## ⚠ Anti-Patterns

> **Warnung — diese Punkte erzeugen Doku-Drift oder Security-Risiken:**

| Anti-Pattern | Warum schlecht |
|--------------|----------------|
| Zwei widersprüchliche Quickstarts ([`README.md`](../README.md) vs [`arctis_ghost_demo_60.md`](arctis_ghost_demo_60.md) vs `init-demo`-README) ohne „Source of Truth“ | Nutzer/Agenten raten |
| Screenshots mit echten Keys oder URLs mit Tokens | Secret-Leak |
| [`DEPLOYMENT_CHECKLIST.md`](../DEPLOYMENT_CHECKLIST.md) abhaken ohne Nachweis (Datum, Umgebung) | Schein-Compliance |
| CI ändern ohne [`CONTRIBUTING.md`](../CONTRIBUTING.md) / Team-Absprache | Überraschungen im PR-Flow |
| Phase wechseln bei Scorecard &lt; 4×1 | A1 vor fertigem A0 |

---

## Optional: CI-Integration (später A1/A2)

> **Hinweis:** Nicht Teil des Mindestplans. Später möglich:

- [`arctis/scripts/launch_check.py`](../arctis/scripts/launch_check.py) als optionaler Workflow-Job (Staging-Secrets nötig)
- Link-Checker für Docs-URLs
- Erweiterung [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) nach Absprache in [`CONTRIBUTING.md`](../CONTRIBUTING.md)

---

## Session-Start & -Ende

**Start einer Agent-Session:** Master-Prompt oben kopieren, `{PHASE}` und `{ID}` setzen, ausführen.

**Ende:** Teilaufgabe erfüllt → Report → **Stopp** → Freigabe für Commit oder nächste ID.

---

*Bei Konflikt mit Produkt-Spec: [`docs/pipeline-a-v1.3.md`](pipeline-a-v1.3.md) und [`docs/RELEASE.md`](RELEASE.md) haben Vorrang für Produktverhalten und Release-Policy.*
