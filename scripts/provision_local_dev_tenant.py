#!/usr/bin/env python3
"""
Provision a local/staging test tenant: DB rows + Pipeline A + workflow, then write .env.

Arctis hat keine öffentlichen REST-Routen POST /api/v1/tenants oder …/keys (siehe
arctis/api/routes/api_keys.py — Stubs). Workflow-POST erfordert pipeline_id,
input_template, owner_user_id — nicht nur name/description/steps.

Dieses Skript:
  1) Legt Tenant + ApiKey (Klartext einmalig ausgeben / in .env) direkt in der DB an.
  2) Ruft dieselbe App-Logik wie HTTP über TestClient auf: POST /pipelines, POST /workflows.

Voraussetzung: DATABASE_URL (z. B. in .env), Schema per Alembic migriert.

Keine Secrets ins Git: .env steht in .gitignore.
"""

from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]


def _load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def _pipeline_a_definition() -> dict[str, Any]:
    from arctis.pipeline_a import build_pipeline_a_ir

    ir = build_pipeline_a_ir()
    steps: list[dict[str, Any]] = []
    for node in ir.nodes.values():
        step: dict[str, Any] = {"name": node.name, "type": node.type, "config": dict(node.config)}
        if node.next:
            assert len(node.next) == 1, node.name
            step["next"] = node.next[0]
        steps.append(step)
    return {"name": ir.name, "steps": steps}


def _merge_env_file(env_path: Path, updates: dict[str, str]) -> None:
    lines: list[str] = []
    if env_path.is_file():
        keys = set(updates)
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            stripped = raw.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                k = stripped.split("=", 1)[0].strip()
                if k in keys:
                    continue
            lines.append(raw.rstrip("\n"))
    while lines and lines[-1] == "":
        lines.pop()
    block = [
        "",
        "# --- Arctis local dev (scripts/provision_local_dev_tenant.py) ---",
    ]
    for k, v in updates.items():
        block.append(f'{k}="{v}"')
    text = "\n".join(lines + block) + "\n"
    env_path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Provision local-dev tenant and write .env")
    parser.add_argument(
        "--tenant-name",
        default="local-dev-tenant",
        help="Unique tenant name (DB unique constraint)",
    )
    parser.add_argument(
        "--workflow-name",
        default="local-dev-workflow",
        help="Workflow name",
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Base URL for Ghost / curl (not used by TestClient)",
    )
    args = parser.parse_args()

    _load_env_file(_REPO / ".env")
    if not os.environ.get("DATABASE_URL"):
        print(
            "ERROR: DATABASE_URL is not set. Add it to .env or the environment "
            "(e.g. sqlite+pysqlite:///./arctis_dev.db) and run Alembic migrations.",
            file=sys.stderr,
        )
        return 1

    if str(_REPO) not in sys.path:
        sys.path.insert(0, str(_REPO))

    from arctis.config import get_settings
    from arctis.constants import SYSTEM_USER_ID
    from arctis.db import SessionLocal, init_engine
    from arctis.api.middleware import hash_api_key_sha256
    from arctis.db.models import ApiKey, Tenant
    from arctis.policy.seed import ensure_default_pipeline_policy
    from fastapi.testclient import TestClient
    from sqlalchemy import select

    get_settings.cache_clear()

    from arctis.app import create_app

    app = create_app()
    init_engine()
    assert SessionLocal is not None

    with SessionLocal() as s:
        ensure_default_pipeline_policy(s)
        existing = s.scalars(select(Tenant).where(Tenant.name == args.tenant_name)).first()
        if existing is not None:
            print(
                f"ERROR: Tenant name {args.tenant_name!r} already exists. "
                "Pick another --tenant-name or remove the tenant from the DB.",
                file=sys.stderr,
            )
            return 1

        tenant_id = uuid.uuid4()
        key_plain = f"arctis_local_{uuid.uuid4().hex}"
        key_row_id = uuid.uuid4()

        s.add(Tenant(id=tenant_id, name=args.tenant_name))
        s.add(
            ApiKey(
                id=key_row_id,
                tenant_id=tenant_id,
                key_hash=hash_api_key_sha256(key_plain),
                active=True,
            ),
        )
        s.commit()

    client = TestClient(app)
    headers = {"X-API-Key": key_plain}

    pr = client.post(
        "/pipelines",
        json={"name": "local-dev-pipeline", "definition": _pipeline_a_definition()},
        headers=headers,
    )
    if pr.status_code != 201:
        print(f"ERROR: POST /pipelines failed: {pr.status_code} {pr.text}", file=sys.stderr)
        return 1
    pipeline_id = pr.json()["id"]

    wf_body = {
        "name": args.workflow_name,
        "pipeline_id": pipeline_id,
        "input_template": {},
        "owner_user_id": str(SYSTEM_USER_ID),
    }
    wf_r = client.post("/workflows", json=wf_body, headers=headers)
    if wf_r.status_code != 201:
        print(f"ERROR: POST /workflows failed: {wf_r.status_code} {wf_r.text}", file=sys.stderr)
        return 1
    workflow_id = wf_r.json()["id"]

    env_path = _REPO / ".env"
    _merge_env_file(
        env_path,
        {
            "ARCTIS_API_URL": args.api_url.rstrip("/"),
            "ARCTIS_API_KEY": key_plain,
            "ARCTIS_TENANT_ID": str(tenant_id),
            "ARCTIS_WORKFLOW_ID": workflow_id,
        },
    )

    print("Provision OK.")
    print(f"  Tenant ID:     {tenant_id}")
    print(f"  API key:       {key_plain[:6]}… (full key only in .env)")
    print(f"  Workflow ID:   {workflow_id}")
    print(f"  .env path:     {env_path}")
    print()
    print("Ghost: set api_base_url in ghost.yaml to ARCTIS_API_URL (or use env ARCTIS_GHOST_API_BASE_URL).")
    print("  export ARCTIS_API_KEY=…   # or load .env in your shell")
    print("  Set workflow_id in ghost.yaml to ARCTIS_WORKFLOW_ID")
    print("  python -m arctis_ghost doctor")
    print("  python -m arctis_ghost run input.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
