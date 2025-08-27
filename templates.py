import os

# Project structure definition (no outer folder)
project_structure = {
    "app.py": "",
    "requirements.txt": "",
    ".env": "OPENAI_API_KEY=\nDB_URL=",
    "frontend": {
        "templates": {
            "index.html": ""
        },
        "static": {
            "style.css": "",
            "script.js": ""
        }
    },
    "backend": {
        "orchestrator.py": "",
        "moderation.py": "",
        "query_engine.py": "",
        "response_generator.py": ""
    },
    "database": {
        "schema.sql": "",
        "laptops.db": "",
        "seed_data.csv": ""
    },
    "docs": {
        "project_documentation.md": ""
    }
}


def create_structure(base_path, structure):
    """
    Recursively creates directories and files for the given project structure.
    """
    for name, content in structure.items():
        path = os.path.join(base_path, name)

        if isinstance(content, dict):
            # Create a directory
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            # Create a file with optional initial content
            with open(path, "w") as f:
                f.write(content)


if __name__ == "__main__":
    base_dir = os.getcwd()  # Current working directory
    create_structure(base_dir, project_structure)
    print("Project structure created successfully in root!")