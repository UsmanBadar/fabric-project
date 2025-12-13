import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[2]
print(ROOT_DIR)
sys.path.append(str(ROOT_DIR))

from config.fabric_core import (login, load_config_from_file, create_capacity, create_workspace,
                                assign_permissions, get_or_create_git_connection, connect_workspace_to_git)





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

    print("===== Creating Capacities =====")

    capacities_config = config["capacities"]
    capacities_defaults_config = config["azure"]["capacity_defaults"]
    resource_group = capacities_defaults_config["resource_group"]

    
    for item in capacities_config:
        create_capacity(item, resource_group, capacities_defaults_config)

    print("===== Creating Workspaces and setting up Git connection =====")

    workspaces_config = config["workspaces"]
    security_groups = config["azure"]["security_groups"]
    github_config = config["github"]


    for item in workspaces_config:
        print(item)
        print(item["permissions"])
        workspace_id = create_workspace(item)
        assign_permissions(workspace_id = workspace_id, permissions = item["permissions"], security_groups = security_groups)
        git_connection_id = get_or_create_git_connection(github_config)
        if git_connection_id:
            connect_workspace_to_git(workspace_id = workspace_id, workspace_name = item["name"], 
                                     directory_name = item["connect_to_git_folder"], git_config = github_config, connection_id = git_connection_id)




if __name__ == "__main__":
    main()