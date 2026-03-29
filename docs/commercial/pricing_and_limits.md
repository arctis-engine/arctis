# A3.1 — Pricing & Limits

Dieses Dokument beschreibt das **Limit- und Nutzungsmodell** aus Sicht von **Tenant** und **Vertrag**. Konkrete Zahlen sind **produkt- und vertragsspezifisch** — hier: Struktur und Anbindung an die Arctis-Implementierung.

---

## Tenant → Limits (Übersicht)

| Dimension | Technische Grundlage (Arctis) | Typische Vertragsdimension |
|-----------|--------------------------------|----------------------------|
| **API-Requests / Durchsatz** | Rate-Limits über Datenbank (`tenant_rate_limits`, `api_key_rate_limits`); Fallback synthetisches Limit in Prod — siehe [`security_production.md`](../security_production.md) | Requests/Minute oder /Tag pro Tenant oder API-Key |
| **Speicher („Storage“)** | Kein zentrales „Blob-Quota“ im Open-Source-Kern: Snapshots/Artefakte hängen von **DB-Größe**, Object-Store (falls angebunden) und eurem Betrieb ab | **Ihr** müsst Limits definieren (z. B. DB-Quota, Attachment-Policy) |
| **Audit-Retention** | `ARCTIS_AUDIT_STORE` (`jsonl` \| `db` \| `none`); JSONL auf Disk oder DB-Tabellen — Retention = **Backup- und Löschpolicy** ([`DR.md`](../DR.md)) | Aufbewahrungsfrist (z. B. Jahre) + Rechtsgrundlage |

**Hinweis:** Eine vollständig **selbstbediente** „Pricing-Seite“ mit automatischer Durchsetzung aller Limits ist **nicht** Bestandteil des Kern-Repos — **Billing-Automatisierung** (Stripe-Nutzung, Metering) bleibt **Backlog** / eure Integrationsaufgabe, sofern nicht separat ausgeliefert.

---

## Fair-Use-Policy (Vorlage)

1. **Bestimmungsgemäße Nutzung:** API und Ghost-CLI für Workflow-Ausführung, Evidence und dokumentierte Integrationen — kein Missbrauch (Scraping fremder Daten, Umgehung von Rate-Limits, Lasttests ohne Absprache).
2. **Geteilte Plattform:** Übermäßige Last, die andere Tenants beeinträchtigt, kann zu **Drosselung** oder Gespräch über höhere Kontingente führen.
3. **Sicherheit:** API-Keys schützen; keine Weitergabe an Dritte ohne Vereinbarung.

**Anpassen** mit eurem Legal/CS und in Verträgen verankern.

---

## Billing & Automatisierung (Backlog)

| Thema | Status im Kern-Repo |
|--------|----------------------|
| Stripe-Integrationen, Billing-Webhooks | Vorhandene Hooks in der API — **Betrieb und Verträge** bei euch |
| Automatische Metering-Abrechnung pro Request | **Backlog** / Custom-Entwicklung |
| Self-Service Plan-Upgrade | **Backlog**, sofern nicht selbst gebaut |

Details zur Paketstrategie: [`arctis_package_strategy.md`](../arctis_package_strategy.md).
