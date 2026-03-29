# A3.2 — SLA & Support

Kundenverständliche **Service-Level**, **Support** und **Statuskommunikation**. Die **konkreten Zeitvorgaben** sind **vertraglich** zwischen euch und dem Kunden festzulegen — unten als **Vorlage** mit Platzhaltern.

---

## Response-Zeiten (Vorlage)

| Priorität | Beispiel-Inhalt | Beispiel-Ziel (nur Platzhalter) |
|-----------|-----------------|----------------------------------|
| **P1 — Kritisch** | Produktionsausfall, keine Authentifizierung möglich, Sicherheitsvorfall | *z. B. Erstreaktion &lt; 1 h* |
| **P2 — Hoch** | Degradation, wiederkehrende Fehler, betroffene Runs | *z. B. Werktags &lt; 4 h* |
| **P3 — Normal** | Fragen, Feature-Wünsche, Dokumentation | *z. B. &lt; 2 Werktage* |

**Messpunkt:** z. B. Eingang in eure Support-Inbox oder Ticketing-System (Zeitstempel).

---

## Eskalation (textueller Ablauf)

1. **Level 1:** Support / Customer Success — Klassifizierung, Workarounds, Link auf Doku.  
2. **Level 2:** Engineering / On-Call — bei P1/P2 oder technischer Blockade.  
3. **Level 3:** Management / Vendor-Eskalation — bei Vertragsfragen, Vorfällen mit Reputation/Risk.

Interne Kontaktdaten und Namen **nicht** in diesem Repo pflegen — nur im Betriebshandbuch.

---

## Statuspage — Semantik

Eine **Statuspage** (z. B. status.example.com) sollte für Kund:innen klar kommunizieren:

| Status | Bedeutung |
|--------|-----------|
| **Operational** | Kern-API und dokumentierte Routen verfügbar im Rahmen des SLA. |
| **Degraded Performance** | Erhöhte Latenz oder Teil-Einschränkungen; Workflows grundsätzlich nutzbar. |
| **Partial Outage** | Bestimmte Funktionen oder Regionen betroffen. |
| **Major Outage** | Kernfunktionen nicht verfügbar. |
| **Maintenance** | Geplante Arbeiten — idealerweise mit Vorankündigung. |

Technische Details der Instanz gehören **nicht** auf die öffentliche Statuspage; nur **kundenrelevante** Komponenten (z. B. „API“, „Execute“, „Dashboard“).

---

## Support-Inbox & Ticket-Flow

| Element | Empfehlung |
|---------|------------|
| **Kanal** | Dedizierte E-Mail (z. B. `support@…`) oder Ticket-Portal — in **Onboarding** und Vertrag nennen. |
| **Pflichtangaben im Ticket** | Tenant-/Kunden-ID (falls vorhanden), Zeitfenster, Request-IDs / `run_id`, **keine** Klartext-API-Keys in E-Mails. |
| **Autoresponse** | Erwartete Antwortzeit verweist auf SLA-Tabelle oben. |

Verknüpfung mit Launch-Prozess: [`Launch_readiness.md`](../Launch_readiness.md) (Support-Inbox als Gate).
