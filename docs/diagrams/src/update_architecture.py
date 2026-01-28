import os

# --- Configuration ---
root_dir = "../../../filip"  # Directory to scan
output_file = "architecture.puml"
ignore_list = {
    ".git",
    ".idea",
    "__pycache__",
    "venv",
    ".mypy_cache",
    "semantics",
    "data",
}
ignore_files = {
    ".DS_Store",
    "__init__.py",
    "setup.py",
    "README.md",
    "LICENSE",
    ".gitignore",
    "custom_types.py",
    "",
}
ignore_file_extensions = {".pyc", ".pyo", ".log", ".tmp", ".bak", ".csv"}

PLANTUML_STYLE = """
!theme materia
skinparam BackgroundColor white

<style>
  Linecolor black
  arrow {
    LineColor #E53027
  }
node {
    Padding 4
    Margin 8
    HorizontalAlignment center
    LineColor #9B231E
    LineThickness 2.0
    BackgroundColor #E53027
    FontColor white
    FontName Roboto
    FontStyle bold
    RoundCorner 3
    MaximumWidth 150
}
</style>
"""


# ---------------------


def generate_wbs(start_path, output):
    output.write("@startwbs\n")
    output.write(PLANTUML_STYLE)

    for root, dirs, files in os.walk(start_path, topdown=True):
        # --- Apply ignore rules ---
        dirs[:] = [d for d in dirs if d not in ignore_list]
        files = [f for f in files if f not in ignore_files]
        # Remove files with ignored extensions
        files = [
            f
            for f in files
            if not any(f.endswith(ext) for ext in ignore_file_extensions)
        ]

        # --------------------------

        # Get the current level and name
        level = root.replace(start_path, "").count(os.sep)

        # Don't print the root folder itself, start with its children
        if level == 0 and root == start_path:
            # Write the root node (project name)
            output.write(f"* {os.path.basename(os.path.abspath(start_path))}\n")

        if level > 0:
            indent = "*" * (level + 1)
            folder_name = os.path.basename(root)
            output.write(f"{indent} {folder_name}\n")

        # Print files at the current level
        file_indent = "*" * (level + 2)
        for f in files:
            output.write(f"{file_indent} {f}\n")

    output.write("@endwbs\n")


if __name__ == "__main__":
    # --- Run the generator ---
    with open(output_file, "w") as f:
        generate_wbs(root_dir, f)

    print(f"Successfully generated '{output_file}'!")
