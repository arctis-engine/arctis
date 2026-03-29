# A3.4 — Release Notes (customer-facing)

Wie ihr **kundenlesbare Release-Informationen** liefern, die mit **technischer Versionierung** und dem **Repository-Changelog** konsistent sind.

---

## Format (customer-facing)

Empfohlene Struktur pro Release:

1. **Version** (z. B. `0.2.0`) und **Datum**  
2. **Kurzüberblick** (2–4 Sätze)  
3. **Added** — neue, sichtbare Fähigkeiten (API, Ghost-CLI)  
4. **Changed** — relevante Verhaltensänderungen (mit Migrationshinweis, falls nötig)  
5. **Fixed** — wesentliche Fehlerkorrekturen  
6. **Security** — nur **öffentlich kommunizierbare** Hinweise (keine CVE-Details ohne Advisory)  
7. **Known limitations** — optional

**Abgrenzung:** Interne Refactorings und reine Teständerungen **nicht** in Kunden-Release-Notes, außer sie ändern garantiertes Verhalten.

---

## Versionierung

- **Quelle der Wahrheit:** [`pyproject.toml`](../../pyproject.toml) — Feld `version`.  
- **Schema:** [Semantic Versioning](https://semver.org/) — `MAJOR.MINOR.PATCH`.  
- **Git-Tags:** Empfehlung `v` + Version, z. B. `v0.1.0` — siehe [`RELEASE.md`](../RELEASE.md).

Kund:innen sollten **Versionsnummer** und **Kompatibilität** (z. B. minimale Ghost-Version) erkennen können.

---

## Changelog-Policy (Repository)

- Das Repository führt [`CHANGELOG.md`](../../CHANGELOG.md) nach **Keep a Changelog**-Stil.  
- **Customer-facing** Release Notes können Auszüge oder Übersetzungen des CHANGELOG sein — müssen aber **redigiert** sein (keine internen Ticket-IDs, keine sensiblen Namen).  
- Breaking Changes: **immer** im CHANGELOG und in Kunden-Notes mit **Migrationshinweis** (Link auf Doku oder Migrationsleitfaden).

---

## Veröffentlichung

- **Ort:** Release-Seite (GitHub/GitLab), E-Mail an Kund:innen, oder Portal — einheitlich verlinken.  
- **Ghost-CLI:** Änderungen an Befehlen oder `ghost.yaml` **explizit** nennen; Link auf [`ghost_cli_reference.md`](../ghost_cli_reference.md).
