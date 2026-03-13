from arctis.v2.router import Router
from arctis.v2.orchestrator import (
    MultiFilePlanner,
    MultiFileExecutor,
    PatchAggregator,
)
from arctis.v2.self_expansion import (
    ExpansionBlueprint,
    ExpansionGenerator,
    ExpansionIntegrator,
    TestBuilder,
)


class V2EntryPoint:
    """
    Zentraler Einstiegspunkt für v2.
    Entscheidet, welche Engine ausgeführt wird.
    """

    def __init__(self, v1_pipeline_callable, llm_callable):
        self.router = Router()
        self.v1_pipeline = v1_pipeline_callable
        self.llm = llm_callable

        # Multi-file components
        self.planner = MultiFilePlanner()
        self.executor = MultiFileExecutor(v1_pipeline_callable)
        self.aggregator = PatchAggregator()

        # Self-expansion components
        self.generator = ExpansionGenerator(llm_callable)
        self.integrator = ExpansionIntegrator()
        self.test_builder = TestBuilder()

    def run(self, task: dict):
        mode = self.router.route(task)

        # 1) SINGLE-FILE → v1-Motor → v2-Validatoren
        if mode == "v1_pipeline":
            patch = self.v1_pipeline(
                file_path=task["files"][0],
                instruction=task["instructions"][task["files"][0]],
                metadata=task.get("metadata", {}),
            )

            validated = self.aggregator.aggregate([patch])
            return validated

        # 2) MULTI-FILE → Orchestrator → Validatoren
        if mode == "v2_orchestrator":
            subtasks = self.planner.plan(task)
            patches = self.executor.execute(subtasks)
            final_patches = self.aggregator.aggregate(patches)
            return final_patches

        # 3) SELF-EXPANSION → Generator → Integrator → Tests
        if mode == "v2_self_expansion":
            blueprint = ExpansionBlueprint(
                target_path=task["target_path"],
                description=task["description"],
                metadata=task.get("metadata", {}),
            )

            raw_code = self.generator.generate(blueprint)
            old_source = task["old_source"]

            final_code = self.integrator.integrate(
                blueprint, old_source, raw_code
            )

            test_code = self.test_builder.build(blueprint)

            return {
                "code": final_code,
                "test": test_code,
            }

        raise Exception(f"Unknown mode: {mode}")
