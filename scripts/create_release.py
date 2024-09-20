import time
import re
import os

def update_version_number():
    current_time_str = time.strftime("%Y%m%d%H%M")
    new_version = f'version = "v{current_time_str}"'
    file_path = "./pyproject.toml"
    with open(file_path, "r") as file:
        content = file.read()
    updated_content = re.sub(r'version = ".*?"', new_version, content)
    with open(file_path, "w") as file:
        file.write(updated_content)
    print(f"Updated version to: v{current_time_str}")

if __name__ == "__main__":
    update_version_number()
    os.system("poetry publish --build")