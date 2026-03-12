# Datei: core/orchestrator.py

from __future__ import annotations

import uuid
import hashlib
from typing import List, Dict, Any, Optional

from core.models import (
    Task,
    Subtask,
    RunRecord,
    PatchMode,
    RunStatus,
)
from core.failures import FailureMode
from core.spec_engine import load_specs, get_rules_for_task
from core.context_manager import select_files_for_task, load_snippets
from core.llm_client import get_llm_client
from core.prompts import (
    build_system_prompt,
    build_user_prompt,
    build_correction_prompt,
)
from core.validator import validate_code, format_validation_errors
from core.patcher import create_patch, apply_patch
from core.plugins.registry import find_plugins_for_task
from core.codebase import create_snapshot, save_snapshot
from core.audit import (
    create_run_folder,
    save_audit,
    save_task,
    save_context,
    save_prompt,
    save_response,
    save_patch_file,
)

MAX_CORRECTION_ITERATIONS = 3


# ============================================================
#  Deterministic Seed
# ============================================================

def deterministic_seed_from(input_hash: str) -> int:
    hex_digest = hashlib.sha256(input_hash.encode("utf-8")).hexdigest()
    return int(hex_digest[:8], 16)


# ============================================================
#  Failure Helper
# ============================================================

def _fail(record: RunRecord, mode: FailureMode) -> RunRecord:
    record.status = RunStatus.FAILED
    record.failure_mode = mode
    return record


# ============================================================
#  LLM Output Normalization
# ============================================================

def _normalize_code_output(raw: str) -> str:
    if not isinstance(raw, str):
        return ""
    return raw.strip()


# ============================================================
#  Single-File Execution Pipeline (v3)
# ============================================================

def _run_single_file_task(
    task: Task,
    spec_profile: Dict[str, Any],
    root: str,
    ctx: Dict[str, Any],
    manifest: Any,
    run_id: str,
) -> RunRecord:

    # 1. Input Hash & Seed
    input_hash = hashlib.sha256(
        f"{task.id}{task.name}{task.description}{manifest}".encode("utf-8")
    ).hexdigest()

    seed = deterministic_seed_from(input_hash)

    record = RunRecord(
        run_id=run_id,
        task_id=task.id,
        input_hash=input_hash,
        seed=seed,
        snapshot_path=f"runs/{run_id}/codebase_manifest.json",
        status=RunStatus.PENDING,
        failure_mode=None,
        files=[],
    )

    # 2. Persist Task & Context
    save_task(task, run_id)
    save_context(ctx, run_id)

    # 3. Build Prompts
    system_prompt = build_system_prompt(spec_profile)
    user_prompt = build_user_prompt(task, ctx, spec_profile)
    save_prompt(user_prompt, run_id)

    client = get_llm_client()
    raw, failure = client.generate(system_prompt, user_prompt, seed)

    if failure:
        return _fail(record, failure)

    code = _normalize_code_output(raw)
    save_response(code, run_id)

    if not code:
        return _fail(record, FailureMode.LLM_EMPTY)

    # 4. Correction Loop
    for iteration in range(MAX_CORRECTION_ITERATIONS):
        validation = validate_code(task, spec_profile, code)

        if validation.ok:
            break

        if iteration == MAX_CORRECTION_ITERATIONS - 1:
            return _fail(record, FailureMode.VALIDATION_FATAL)

        errors_summary = format_validation_errors(validation)
        correction_prompt = build_correction_prompt(task, ctx, spec_profile, errors_summary)
        save_prompt(correction_prompt, run_id, iteration=iteration + 1)

        correction_seed = seed + iteration + 1
        raw, failure = client.generate(system_prompt, correction_prompt, correction_seed)

        if failure:
            return _fail(record, failure)

        code = _normalize_code_output(raw)
        save_response(code, run_id, iteration=iteration + 1)

        if not code:
            return _fail(record, FailureMode.LLM_EMPTY)

    # 5. Apply Patch
    try:
        print("DEBUG: creating patch")
        patch = create_patch(
            target_file=task.target_file,
            new_content=code,
            root=root,
            mode=PatchMode.FILE,
        )

        print("DEBUG: applying patch")
        failure = apply_patch(patch, root)
        print("DEBUG: apply_patch returned:", failure)

        if failure:
            print("DEBUG: failure inside apply_patch")
            return _fail(record, failure)

        if task.target_file:
            suffix = task.target_file.replace("/", "_").replace(".", "_")
        else:
            suffix = "unknown"

        print("DEBUG: saving patch file")
        save_patch_file(patch, run_id, suffix=suffix)

        if task.target_file:
            record.files.append({"path": task.target_file})

    except Exception as e:
        import traceback
        print("\n" + "="*70)
        print("PATCH BLOCK EXCEPTION CAUGHT")
        print("- Exception:", repr(e))
        print("- Type:", type(e).__name__)
        print("- Location: inside apply-patch block")
        print("="*70)
        traceback.print_exc()
        print("="*70 + "\n")
        return _fail(record, FailureMode.IO_ERROR)

    # 6. Success
    record.status = RunStatus.SUCCESS
    save_audit(record, run_id)
    return record


# ============================================================
#  Main Orchestrator (v3)
# ============================================================

def run_task(
    task: Task,
    root: str,
    file_metas: Optional[List[Dict[str, Any]]] = None,
) -> RunRecord:

    run_id = uuid.uuid4().hex
    create_run_folder(run_id)

    # 1. Load Specs
    try:
        raw_specs = load_specs(root)
        spec_profile = get_rules_for_task(raw_specs, task)
    except Exception:
        spec_profile = {"effective": {}}

    # 2. Snapshot
    try:
        manifest = create_snapshot(root)
        save_snapshot(manifest, run_id)
    except Exception:
        record = RunRecord(
            run_id=run_id,
            task_id=task.id,
            input_hash="",
            seed=0,
            snapshot_path="",
            status=RunStatus.FAILED,
            failure_mode=FailureMode.IO_ERROR,
            files=[],
        )
        save_audit(record, run_id)
        return record

    # 3. Plugin Routing (Multi-File)
    plugins = find_plugins_for_task(task)

    if plugins:
        plugin = plugins[0]
        result = plugin.safe_execute(task, spec_profile, {})

        if result.failure:
            record = RunRecord(
                run_id=run_id,
                task_id=task.id,
                input_hash="",
                seed=0,
                snapshot_path=f"runs/{run_id}/codebase_manifest.json",
                status=RunStatus.FAILED,
                failure_mode=result.failure,
                files=[],
            )
            save_audit(record, run_id)
            return record

        records: List[RunRecord] = []

        for sub in result.subtasks:
            selected = select_files_for_task(sub, spec_profile, file_metas or [])
            ctx = load_snippets(selected, root)

            rec = _run_single_file_task(
                task=sub,
                spec_profile=spec_profile,
                root=root,
                ctx=ctx,
                manifest=manifest,
                run_id=run_id,
            )
            records.append(rec)

        failed = [r for r in records if r.status != RunStatus.SUCCESS]
        all_files: List[Dict[str, Any]] = []
        for r in records:
            all_files.extend(r.files)

        summary = RunRecord(
            run_id=run_id,
            task_id=task.id,
            input_hash=records[0].input_hash if records else "",
            seed=records[0].seed if records else 0,
            snapshot_path=f"runs/{run_id}/codebase_manifest.json",
            status=RunStatus.FAILED if failed else RunStatus.SUCCESS,
            failure_mode=failed[0].failure_mode if failed else None,
            files=all_files,
        )
        save_audit(summary, run_id)
        return summary

    # 4. Single-File Task
    selected = select_files_for_task(task, spec_profile, file_metas or [])
    ctx = load_snippets(selected, root)

    return _run_single_file_task(
        task=task,
        spec_profile=spec_profile,
        root=root,
        ctx=ctx,
        manifest=manifest,
        run_id=run_id,
    )
