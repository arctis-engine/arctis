# Customer Onboarding Kit (A2.4)

Kurzfassung für **Kund:innen und Integrationspartner** — ohne die Pflicht, das gesamte Repository zu kennen.  
Technische Tiefe: verlinkte Dokumente unter `docs/`.

---

## Startpfade (ohne Repo)

| Weg | Dokumentation |
|-----|----------------|
| **Container** | [`Packaging.md`](../Packaging.md) — A2.1 Docker |
| **Python-Paket (Wheel)** | [`Packaging.md`](../Packaging.md) — A2.2 |
| **Gehostete API (SaaS)** | [`Packaging.md`](../Packaging.md) — A2.3; Basis-URL und API-Key von euch |

## Commercial Readiness (Phase A3)

Pricing, SLA, Evidence-Kernbotschaften, Release-Policy für Vertrieb und Vertrag: **[`../commercial/README.md`](../commercial/README.md)**.

---

## Ghost CLI (Customer-Execute)

1. **Schnell:** [`ghost_quickstart.md`](../ghost_quickstart.md)  
2. **60-Sekunden-Story:** [`arctis_ghost_demo_60.md`](../arctis_ghost_demo_60.md)  
3. **Kommandos im Detail:** [`ghost_cli_reference.md`](../ghost_cli_reference.md)  
4. **Beispiel-Execute-JSON:** [`examples/customer_execute_body.json`](../examples/customer_execute_body.json)

---

## Evidence & Nachweis

- Demo-Matrix (Skills, Routing): [`demo_matrix.md`](../demo_matrix.md)  
- Sicherheit & API-Verhalten: [`security_production.md`](../security_production.md)  
- Deployment (Betreiber): [`Deployment.md`](../Deployment.md)

---

## Troubleshooting (erste Schritte)

| Symptom | Hinweis |
|---------|---------|
| `401` / „Invalid API key“ | Key aktiv, nicht abgelaufen; Header `X-API-Key` gesetzt. |
| `503` / DB nicht initialisiert | API ohne funktionierende `DATABASE_URL` / Migration — Betreiber: `alembic upgrade head`. |
| `ghost doctor` /health rot | Falsche URL oder API nicht erreichbar; Firewall/TLS. |
| CORS-Fehler im Browser | `ALLOWED_ORIGINS` muss euer Frontend-Origin enthalten — Betreiber. |

CLI-Details und Pfade: [`ghost_cli_reference.md`](../ghost_cli_reference.md).  
Mitwirkung und Tests (für Entwickler:innen mit Repo): [`CONTRIBUTING.md`](../../CONTRIBUTING.md).
