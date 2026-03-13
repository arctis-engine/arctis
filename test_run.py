from arctis.module import run

task = {
    "mode": "v1",
    "files": [
        "dev/flask/src/flask/app.py"
    ],
    "instructions": {
        "dev/flask/src/flask/app.py": (
            "Füge folgende Helper-Funktion am Ende der Datei hinzu:\n\n"
            "def is_debug_mode(app):\n"
            "    return app.debug"
        )
    },
    "metadata": {
        "patch_mode": "append"
    }
}

results = run(task)
result = results[0]

print("\n--- ARCTIS RESULT ---\n")
print("File:", result.file_path)
print("Mode:", result.mode)
print("\n--- NEW SOURCE PREVIEW ---\n")
print(result.new_source[:500])
print("\n--- END ---\n")
