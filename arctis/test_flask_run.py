from arctis.v2.flask_runner import run_flask_instruction
from arctis.llm.ollama_client import OllamaClient


def main():
    repo_root = "sandbox_v3"
    instruction = "Add a GET /users route that returns a list of users"

    llm = OllamaClient(model="qwen2.5-coder:latest")


    results = run_flask_instruction(
        repo_root=repo_root,
        instruction=instruction,
        llm_client=llm,
    )

    for r in results:
        print("\n--- FILE:", r.file_path)
        print("--- MODE:", r.mode)
        print("--- GENERATED CODE:\n")
        print(r.new_source)
        print("\n------------------------\n")


if __name__ == "__main__":
    main()
