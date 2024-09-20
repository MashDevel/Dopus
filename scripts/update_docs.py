import importlib
import inspect
import os
import sys
from pathlib import Path
import shutil
from typing import Set, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
API_DIR = DOCS_DIR / "api"
GENERATED_COMMENT = "<!-- This file is auto-generated. Do not edit it directly. -->\n\n"


def update_module_docs(module_name: str) -> None:
    """
    Generate documentation for the specified module.

    This function imports the module, extracts classes and decorated functions,
    generates corresponding markdown files, updates the API index, and manages
    documentation assets.

    Args:
        module_name (str): The name of the module to document.
    """
    module = importlib.import_module(module_name)
    classes = inspect.getmembers(module, inspect.isclass)
    decorators = [
        obj for name, obj in inspect.getmembers(module)
        if callable(obj) and name == 'tool'
    ]
    processed_files: Set[str] = set()
    api_index_content = "# API Reference\n\n"

    API_DIR.mkdir(parents=True, exist_ok=True)

    # Process classes
    for name, cls in classes:
        markdown_content = f"""{GENERATED_COMMENT}# {name}

::: {module_name}.{name}
"""
        file_name = f"{name.lower()}.md"
        file_path = API_DIR / file_name
        file_path.write_text(markdown_content, encoding='utf-8')
        processed_files.add(file_name)

        api_index_content += f"- [{name}](api/{file_name})\n"

    # Process tool decorator
    if decorators:
        tool_decorator = decorators[0]
        markdown_content = f"""{GENERATED_COMMENT}# tool

::: {module_name}.tool
"""
        file_name = "tool.md"
        file_path = API_DIR / file_name
        file_path.write_text(markdown_content, encoding='utf-8')
        processed_files.add(file_name)

        api_index_content += f"- [tool](api/{file_name})\n"

    # Remove outdated files
    for file_path in API_DIR.glob('*.md'):
        if file_path.name not in processed_files:
            file_path.unlink()

    # Copy README.md to docs/README.md and add generated comment
    copy_file_with_comment(PROJECT_ROOT / "README.md", DOCS_DIR / "README.md")

    # Copy CONTRIBUTING.md to docs/CONTRIBUTING.md and add generated comment
    copy_file_with_comment(PROJECT_ROOT / "CONTRIBUTING.md", DOCS_DIR / "CONTRIBUTING.md")

    # Write API index
    api_index_content = GENERATED_COMMENT + api_index_content
    (DOCS_DIR / "api.md").write_text(api_index_content, encoding='utf-8')


def copy_file_with_comment(source_path: Path, destination_path: Path) -> None:
    """
    Copy a file to the destination path with a generated comment prepended.

    Args:
        source_path (Path): The path to the source file.
        destination_path (Path): The path to the destination file.
    """
    content = source_path.read_text(encoding='utf-8')
    destination_path.write_text(GENERATED_COMMENT + content, encoding='utf-8')


def get_tool_decorator(module) -> List[Tuple[str, callable]]:
    """
    Retrieve the tool decorators from the module.

    Args:
        module: The module to inspect.

    Returns:
        List of tuples containing the name and the decorator object.
    """
    return [
        (name, obj) for name, obj in inspect.getmembers(module)
        if callable(obj) and name == 'tool'
    ]


if __name__ == "__main__":
    MODULE_NAME = "dopus.core"
    try:
        update_module_docs(MODULE_NAME)
        print(f"Documentation for module '{MODULE_NAME}' has been updated successfully.")
    except Exception as e:
        print(f"An error occurred while updating documentation: {e}", file=sys.stderr)
        sys.exit(1)