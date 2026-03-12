from core.models import Task
from core.orchestrator import run_task

task = Task(
    id="t5",
    name="Create module",
    type="codegen.multi_file",
    description="Create a simple Python module with two files: utils.py containing a function greet(name), and main.py that imports greet and prints the greeting.",
    target_file=None,
)

result = run_task(task, root="sandbox_v3")
print(result)
