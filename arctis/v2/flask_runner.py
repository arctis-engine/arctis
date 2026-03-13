from typing import List

from arctis.context import RepoContextEngine
from arctis.context.context_models import RepoContext
from arctis.planner import TaskPlanner, MicroTask as PlannerTask
from arctis.micro_pipeline import (
    MicroTask as PipelineTask,
    MicroResult,
    run_micro_pipeline,
)


def build_context(repo_root: str) -> RepoContext:
    engine = RepoContextEngine(repo_root)
    return engine.build()


def plan_flask_tasks(ctx: RepoContext, instruction: str) -> List[PlannerTask]:
    planner = TaskPlanner(ctx)
    return planner.plan(instruction)


def _to_pipeline_task(task: PlannerTask) -> PipelineTask:
    """
    Adapter: PlannerTask → PipelineTask (v1 micro_pipeline)
    """
    return PipelineTask(
        file_path=task.file_path,
        instruction=task.instruction,
        mode=task.mode if hasattr(task, "mode") else "generate",
        old_source=None,
        metadata=task.metadata if hasattr(task, "metadata") else None,
    )


def run_flask_instruction(
    repo_root: str,
    instruction: str,
    llm_client,
) -> List[MicroResult]:
    """
    End-to-end Flask v2 pipeline:
    - baut RepoContext
    - plant Flask-MicroTasks
    - ruft deine bestehende micro_pipeline auf
    """
    ctx = build_context(repo_root)
    planner_tasks = plan_flask_tasks(ctx, instruction)

    results: List[MicroResult] = []

    for pt in planner_tasks:
        pipeline_task = _to_pipeline_task(pt)
        result = run_micro_pipeline(pipeline_task, llm_client)
        results.append(result)

    return results
