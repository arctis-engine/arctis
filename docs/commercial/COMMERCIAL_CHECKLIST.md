# A3.5 — Commercial Checklist

Vor **kommerziellem Go-Live** oder **Enterprise-Angebot** abhaken. Mit **N/A** und Begründung, wenn ein Punkt für euer Modell nicht gilt.

---

## A3.1 — Pricing & Limits

- [ ] **Tenant → Limits** in [`pricing_and_limits.md`](pricing_and_limits.md) beschrieben (oder vertraglich woanders, hier verlinkt)
- [ ] **Fair-Use-Policy** angepasst und rechtlich geprüft
- [ ] **Billing-Automatisierung:** Backlog dokumentiert oder Lösung live

## A3.2 — SLA & Support

- [ ] **Response-Zeiten** (P1–P3) vertraglich oder in Anlage festgelegt
- [ ] **Eskalationspfad** intern beschrieben und dem Support bekannt
- [ ] **Statuspage** betrieben; Semantik mit [`sla_and_support.md`](sla_and_support.md) konsistent
- [ ] **Support-Inbox** / Ticketsystem erreichbar und in Onboarding genannt

## A3.3 — Evidence Bundle

- [ ] [`evidence_bundle.md`](evidence_bundle.md) für Kund:innen freigegeben (keine internen Details)
- [ ] Abgleich mit [`security_production.md`](../security_production.md), [`DR.md`](../DR.md), [`Observability.md`](../Observability.md) — nur kundenverträgliche Kurzfassungen

## A3.4 — Release Notes

- [ ] **Format** und Verantwortlichkeit für customer-facing Notes festgelegt
- [ ] **Versionierung** mit `pyproject.toml` / Tags abgestimmt ([`RELEASE.md`](../RELEASE.md))
- [ ] **CHANGELOG** wird vor Release gepflegt ([`CHANGELOG.md`](../../CHANGELOG.md))

## Konsistenz

- [ ] [`../customer/README.md`](../customer/README.md) verweist auf Commercial-Doku
- [ ] Kein Widerspruch zwischen README, Ghost-Demos und Commercial-Texten

---

## Gate A3 (strategisch)

Arctis ist **verkaufbar**, wenn Pricing/Limits, SLA/Support, Evidence-/Security-Kernbotschaften, Release-Policy und diese Checkliste **reviewt** und für den Vertrieb freigegeben sind.
