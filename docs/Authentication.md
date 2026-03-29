# Authentication & Identity (A1.3)

Diese Seite beschreibt **zwei Ebenen**: die **implementierte** Control-Plane-Auth per **API-Key** und die **IdP-Wahl** (Auth0 **oder** Supabase) für menschliche Anmeldung / Dashboard — inklusive der Variablen, die [`launch_check`](../arctis/scripts/launch_check.py) prüft.

---

## 1. Control Plane API (maschinell) — implementiert

| Mechanismus | Details |
|-------------|---------|
| Header | `X-API-Key` mit Klartext-Key; serverseitig SHA-256-Hash, Abgleich mit Tabelle `api_keys` ([`arctis/api/middleware.py`](../arctis/api/middleware.py)). |
| Öffentliche Routen | u. a. `GET /health`; OpenAPI nur wenn [`ARCTIS_EXPOSE_OPENAPI`](security_production.md) es erlaubt. |
| Tenant | Jeder gültige Key ist an `tenant_id` gebunden; Scopes über `scopes` ([`arctis/auth/scopes.py`](../arctis/auth/scopes.py)). |
| JWT | Die FastAPI-App **validiert keine** Endnutzer-JWTs für den regulären REST-Zugriff — Integrationen nutzen **API-Keys**. |

**Tests:** `pytest tests/api/` (mit DB-Fixtures) deckt AuthZ und Scopes ab.

---

## 2. Auth0 oder Supabase (Dashboard / Identity-Umgebung)

[`python -m arctis.scripts.launch_check`](../arctis/scripts/launch_check.py) verlangt in Schritt **„[7/11] Auth0 or Supabase“** **entweder** das vollständige **Auth0**-Set **oder** das **Supabase**-Set — Namen exakt wie im Skript:

**Auth0 (alle setzen):**

- `AUTH0_SECRET`
- `AUTH0_BASE_URL`
- `AUTH0_ISSUER_BASE_URL`
- `AUTH0_CLIENT_ID`
- `AUTH0_CLIENT_SECRET`

**Supabase (alle setzen):**

- `NEXT_PUBLIC_SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

> Werte nur im Secret Store; nie in Git committen.

Die konkrete **Dashboard-App** kann außerhalb dieses Repos liegen; die Variablen versorgen gängige Auth0-/Supabase-Integrationen (z. B. Next.js). **JWT-Validierung** für Browser-Sessions erfolgt typischerweise **im Frontend oder SSR** über die IdP-SDKs, nicht über eine zentrale JWT-Middleware in `arctis` für alle API-Routen.

---

## 3. Callbacks und erlaubte URLs (IdP-Konsole)

Im **Auth0-Dashboard** bzw. **Supabase-Projekt** konfigurieren (Bezeichnungen je nach UI):

| Thema | Was eintragen |
|--------|----------------|
| **Callback / Redirect** | HTTPS-URL des Dashboards nach Login, z. B. `https://<dashboard-host>/callback` oder Framework-Standard (Auth0: *Allowed Callback URLs*). |
| **Logout** | Passende Logout-Redirect-URL (*Allowed Logout URLs*). |
| **Web Origin / Site URL** | Origin des Dashboards; muss zu den Aufrufen der **Arctis-API** passen; API-seitig zusätzlich [`ALLOWED_ORIGINS`](Deployment.md) für Browser-`fetch` vom Frontend. |

**JWT-Validierung „getestet“:** Im IdP-typischen Flow: Login im Browser → Token vom SDK → geschützte Dashboard-Routen. Für die **REST-API** weiterhin **API-Key**-Tests wie oben; ein E2E-Lauf (`launch_check` → Playwright) setzt voraus, dass `dashboard/` ein `npm run test:e2e` anbietet, sobald die UI angebunden ist.

---

## 4. Tenant-Setup

| Thema | Hinweis |
|--------|---------|
| **Tenant in der DB** | `Tenant`- und `ApiKey`-Zeilen (siehe [`arctis/db/models.py`](../arctis/db/models.py)); Keys ohne gesetzte `scopes` erhalten Default-Scopes ([`default_legacy_scopes`](../arctis/auth/scopes.py)). |
| **Ghost / Customer** | Kunden nutzen `X-API-Key` im gleichen Tenant-Modell; siehe [README](../README.md), [security_production.md](security_production.md). |

---

## 5. Weiterlesen

- [security_production.md](security_production.md) — Scopes, CORS, unsichere Dev-Flags  
- [Deployment.md](Deployment.md) — Secrets (A1.2), Infrastruktur (A1.1)  
- [arctis-indie-launch-v1.md](arctis-indie-launch-v1.md) — Indie-Launch, Auth-Optionen (nicht normativ für Pipeline-Spec)
