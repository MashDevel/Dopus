import importlib
import inspect
import os
import sys
import shutil

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

docs_dir = os.path.join(project_root, "docs")

def update_module_docs(module_name):
    module = importlib.import_module(module_name)
    classes = inspect.getmembers(module, inspect.isclass)
    decorators = [obj for name, obj in inspect.getmembers(module) if callable(obj) and name == 'tool']
    processed_files = set()
    api_index_content = "# API Reference\n\n"

    api_dir = os.path.join(docs_dir, "api")
    os.makedirs(api_dir, exist_ok=True)

    generated_comment = "<!-- This file is auto-generated. Do not edit it directly. -->\n\n"

    # Process classes
    for name, cls in classes:
        markdown_content = f"""{generated_comment}# {name}

::: {module_name}.{name}
"""
        file_name = f"{name.lower()}.md"
        file_path = os.path.join(api_dir, file_name)
        with open(file_path, 'w') as f:
            f.write(markdown_content)
        processed_files.add(file_name)
        
        api_index_content += f"- [{name}](api/{file_name})\n"

    # Process tool decorator
    if decorators:
        tool_decorator = decorators[0]
        markdown_content = f"""{generated_comment}# tool

::: {module_name}.tool
"""
        file_name = "tool.md"
        file_path = os.path.join(api_dir, file_name)
        with open(file_path, 'w') as f:
            f.write(markdown_content)
        processed_files.add(file_name)
        
        api_index_content += f"- [tool](api/{file_name})\n"

    # Remove outdated files
    for file_name in os.listdir(api_dir):
        if file_name.endswith('.md') and file_name not in processed_files:
            file_path = os.path.join(api_dir, file_name)
            os.remove(file_path)

    # Copy README.md to docs/index.md and add generated comment
    readme_path = os.path.join(project_root, "README.md")
    docs_index_path = os.path.join(docs_dir, "README.md")
    copy_file_with_comment(readme_path, docs_index_path)

    # Copy CONTRIBUTING.md to docs/contributing.md and add generated comment
    contributing_path = os.path.join(project_root, "CONTRIBUTING.md")
    docs_contributing_path = os.path.join(docs_dir, "CONTRIBUTING.md")
    copy_file_with_comment(contributing_path, docs_contributing_path)

    # Write API index
    api_index_content = generated_comment + api_index_content
    api_index_path = os.path.join(docs_dir, "api.md")
    with open(api_index_path, 'w') as f:
        f.write(api_index_content)

def copy_file_with_comment(source_path, destination_path):
    generated_comment = "<!-- This file is auto-generated. Do not edit it directly. -->\n\n"
    with open(source_path, 'r') as source_file:
        content = source_file.read()
    with open(destination_path, 'w') as destination_file:
        destination_file.write(generated_comment + content)

if __name__ == "__main__":
    module_name = "dopus.core"
    update_module_docs(module_name)