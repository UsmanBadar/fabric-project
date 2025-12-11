import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[2]
print(ROOT_DIR)
sys.path.append(str(ROOT_DIR))

from config.fabric_core import login, load_config_from_file, create_capacity





def main():

    print("===== Azure Login =====")

    login()

    print("===== Loading config file =====")

    template_file_path = Path(__file__).parent.parent / "templates" / "v01" / "v01_template.yaml"

    if template_file_path.exists():
        config = load_config_from_file(template_file_path)
        print("===config file loaded===")
    else:
        raise RuntimeError("Config file not found.")
    
    capacities_config = config["capacities"]
    capacities_defaults_config = config["azure"]["capacity_defaults"]
    resource_group = capacities_defaults_config["resource_group"]
    
    for item in capacities_config:
        create_capacity(item, resource_group, capacities_defaults_config)



if __name__ == "__main__":
    main()