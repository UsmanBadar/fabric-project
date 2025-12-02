"""
This file loads the YAML config file for creating the resources
"""
from pathlib import Path
import yaml, os
from string import Template
from fabric_core import load_local_env_file


load_local_env_file()

def load_config_from_file(file_path: str) -> dict:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {file_path}")

    yaml_content = path.read_text()

    temp_config = yaml.safe_load(yaml_content) or {}
    solution_version = str(temp_config.get("solution_version", "av01"))

    yaml_with_version = yaml_content.replace(
        "{{SOLUTION_VERSION}}",
        solution_version,
    )

    final_config = Template(yaml_with_version).safe_substitute(os.environ)

    return yaml.safe_load(final_config)

    