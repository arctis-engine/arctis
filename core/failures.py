from __future__ import annotations

from enum import Enum
from typing import Optional


FAILURE_VERSION = 3


class FailureCategory(str, Enum):
    LLM = "llm"
    VALIDATION = "validation"
    PATCH = "patch"
    CONTEXT = "context"
    SPEC = "spec"
    PLUGIN = "plugin"
    IO = "io"
    INTERNAL = "internal"
    UNKNOWN = "unknown"


class FailureMode(str, Enum):
    # LLM-bezogene Fehler
    LLM_TIMEOUT = "llm_timeout"
    LLM_EMPTY = "llm_empty"
    LLM_MALFORMED = "llm_malformed"
    LLM_UNAVAILABLE = "llm_unavailable"

    # Validierung
    VALIDATION_ERROR = "validation_error"
    VALIDATION_FATAL = "validation_fatal"

    # Patch / Schreiben
    PATCH_HASH_MISMATCH = "patch_hash_mismatch"
    PATCH_INVALID_CODE = "patch_invalid_code"
    PATCH_APPLY_FAILED = "patch_apply_failed"

    # Kontext / Dateien
    CONTEXT_LOAD_FAILED = "context_load_failed"
    CONTEXT_FILE_MISSING = "context_file_missing"
    CONTEXT_TOO_LARGE = "context_too_large"

    # Spezifikationen
    SPEC_INVALID = "spec_invalid"
    SPEC_MISSING = "spec_missing"

    # Plugins / Brains
    PLUGIN_INVALID_SUBTASK = "plugin_invalid_subtask"
    PLUGIN_RUNTIME_ERROR = "plugin_runtime_error"

    # IO / System
    IO_ERROR = "io_error"
    INTERNAL_ERROR = "internal_error"

    # Fallback
    UNKNOWN = "unknown"


def failure_category(mode: Optional[FailureMode]) -> FailureCategory:
    if mode is None:
        return FailureCategory.UNKNOWN

    if mode in {
        FailureMode.LLM_TIMEOUT,
        FailureMode.LLM_EMPTY,
        FailureMode.LLM_MALFORMED,
        FailureMode.LLM_UNAVAILABLE,
    }:
        return FailureCategory.LLM

    if mode in {
        FailureMode.VALIDATION_ERROR,
        FailureMode.VALIDATION_FATAL,
    }:
        return FailureCategory.VALIDATION

    if mode in {
        FailureMode.PATCH_HASH_MISMATCH,
        FailureMode.PATCH_INVALID_CODE,
        FailureMode.PATCH_APPLY_FAILED,
    }:
        return FailureCategory.PATCH

    if mode in {
        FailureMode.CONTEXT_LOAD_FAILED,
        FailureMode.CONTEXT_FILE_MISSING,
        FailureMode.CONTEXT_TOO_LARGE,
    }:
        return FailureCategory.CONTEXT

    if mode in {
        FailureMode.SPEC_INVALID,
        FailureMode.SPEC_MISSING,
    }:
        return FailureCategory.SPEC

    if mode in {
        FailureMode.PLUGIN_INVALID_SUBTASK,
        FailureMode.PLUGIN_RUNTIME_ERROR,
    }:
        return FailureCategory.PLUGIN

    if mode in {
        FailureMode.IO_ERROR,
    }:
        return FailureCategory.IO

    if mode in {
        FailureMode.INTERNAL_ERROR,
    }:
        return FailureCategory.INTERNAL

    return FailureCategory.UNKNOWN
