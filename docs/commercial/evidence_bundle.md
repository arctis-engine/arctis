# A3.3 — Evidence Bundle (customer-facing)

**Zweck:** Kund:innen und Prüfern zeigen, **wie** Nachweise zu Runs entstehen — **ohne** interne Implementierungsdetails oder Admin-Pfade.

---

## Architektur (textuell)

1. **Ausführung:** Geschäftsdaten werden als **Execute-Request** an die Arctis-API übergeben (`POST` auf die dokumentierte Customer-Execute-Route).  
2. **Ausführung & Governance:** Die **gleiche** serverseitige Pipeline wendet Policy, Routing und Budgets an — **keine** zweite Wahrheit im Client.  
3. **Run-Objekt:** Der Lauf ist unter einer **Run-ID** abrufbar; Status und Zusammenfassung über die API.  
4. **Evidence:** Strukturierte Nachweise (Input/Output, Routing, Kosten, Skills) werden im **Evidence-Kontext** der Anwendung bereitgestellt — abrufbar über dokumentierte Endpunkte bzw. über die **Ghost-CLI** (`evidence`, `pull-artifacts`, `verify`).  
5. **Lokale Artefakte (optional):** Mit `pull-artifacts` können **Envelope** und **Skill-Reports** unter konfigurierbarem `outgoing/` geschrieben werden — für Audits und Offline-Reviews.

Kein direkter Engine-Import im Ghost-Client; Kommunikation **HTTP-only** — siehe [`ghost_cli_reference.md`](../ghost_cli_reference.md).

---

## Security (Kurzfassung, customer-safe)

- **Authentifizierung** über **API-Keys** (`X-API-Key`), tenant-gebunden; Keys sind wie Secrets zu behandeln.  
- **Transport:** HTTPS in Produktion; CORS nur für explizit erlaubte Origins (`ALLOWED_ORIGINS`).  
- **Keine** Speicherung von API-Keys in öffentlichen Repos; Ghost empfiehlt Umgebungsvariablen.  
- Details: [`security_production.md`](../security_production.md) (technisch), [`Authentication.md`](../Authentication.md).

---

## Disaster Recovery (Kurzfassung, customer-safe)

- Datenhaltung primär in der **von euch betriebenen Datenbank**; Wiederherstellung und Backups sind **Betriebsverantwortung**.  
- RPO/RTO sind **vertraglich** bzw. im DPA mit euch zu definieren — Orientierung: [`DR.md`](../DR.md) (nur für Betreiber im Detail).

---

## Observability (Kurzfassung, customer-safe)

- **Fehleranalyse** kann über ein angebundenes **Error-Tracking** (z. B. Sentry) erfolgen — ohne Roh-PII in Tickets, je nach eurer Konfiguration.  
- **Metriken** können betrieblich ausgewertet werden (Latenz, Fehlerquoten); Kund:innen sehen typischerweise **Statuspage** und Support-Antworten, nicht interne Dashboards.

Details nur intern: [`Observability.md`](../Observability.md).

---

## Audit-Mechanismen (customer-safe)

- **Audit-Export** und Speicherort hängen von der Konfiguration ab (`ARCTIS_AUDIT_STORE`, ggf. JSONL-Verzeichnis oder Datenbank) — siehe [`Deployment.md`](../Deployment.md), [`DR.md`](../DR.md).  
- **Zweck:** Nachvollziehbarkeit für Compliance; **Umfang** und **Aufbewahrung** sind mit euch abzustimmen.

---

## Was hier absichtlich fehlt

- Interne Hostnamen, Admin-Credentials, Repo-Interna  
- Vollständige JSON-Schemas (stehen in produktnaher Doku / OpenAPI, wo freigegeben)
