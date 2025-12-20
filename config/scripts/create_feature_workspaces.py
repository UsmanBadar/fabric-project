import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json

from config.fabric_core import (set_stdout_encoding_to_utf_8, load_local_env_file, load_config_from_file,
                                login, create_workspace, get_or_create_git_connection, assign_permissions,
                                connect_workspace_to_git, update_workspace_from_git, get_fab_cli_executable_path,
                                run_fabric_cli_command)




set_stdout_encoding_to_utf_8()

def get_capacity_for_workspace_type(workspace_type: str, solution_version: str) -> str:
    capacity_map = {
        "processing" : f"fc{solution_version}devengineering",
        "datastores" : f"fc{solution_version}devengineering",
        "consumption" : f"fc{solution_version}devconsumption"
    }

    return capacity_map.get(workspace_type, None)

def main():

    load_local_env_file()

    
    feature_branch = os.getenv("FEATURE_BRANCH_NAME")
    workspaces_input = os.getenv("WORKSPACES_TO_CREATE", "processing,datastores")

    workspace_types = [ws.strip() for ws in workspaces_input.split(",") if ws.strip()]


    config = load_config_from_file("config/templates/v01/v01-template.yml")

    solution_version = config.get(solution_version, "av01")
    azure_config = config.get("azure", {})
    security_groups = config.get("security_groups", {})
    git_config = config.get("github", {})


    git_config["branch"] = feature_branch

    print("=== AUTHENTICATING ===")

    login()

    print(
        f"\n=== CREATING FEATURE WORKSPACES FOR BRANCH: {feature_branch} ===")
    
    github_connection_id = None

    for workspace_type in workspace_types:
        # Construct workspace name: <solution_version>-<branch>-<type>
        workspace_name = f"{solution_version}-{feature_branch}-{workspace_type}"

        # Get capacity for this workspace type
        capacity_name = get_capacity_for_workspace_type(
            workspace_type, solution_version)

        if not capacity_name:
            print(f"✗ Unknown workspace type: {workspace_type}")
            continue

        print(f"\n--- Creating {workspace_name} ---")

        # Create workspace
        workspace_config = {
            'name': workspace_name,
            'capacity': capacity_name
        }
        workspace_id = create_workspace(workspace_config)

        if workspace_id:
            # Assign Engineers as Contributors
            permissions = [{'group': 'SG_AV_Engineers', 'role': 'Admin'}]
            assign_permissions(workspace_id, permissions, security_groups)

            # Connect to Git (feature branch, solution/<type>/ folder)
            if not github_connection_id:
                github_connection_id = get_or_create_git_connection(git_config)

            if github_connection_id:
                git_directory = f"solution/{workspace_type}/"
                success = connect_workspace_to_git(
                    workspace_id,
                    workspace_name,
                    git_directory,
                    git_config,
                    github_connection_id
                )

                if success:
                    # Initialize the connection
                    init_response = run_fabric_cli_command([
                        'api', '-X', 'post',
                        f'workspaces/{workspace_id}/git/initializeConnection',
                        '-i', '{}'
                    ])
                    print(f"  ✓ Initialized Git connection")

                    # Pull content from Git into the workspace
                    update_workspace_from_git(workspace_id, workspace_name)

    print("\n✓ Feature workspace creation complete")


if __name__ == "__main__":
    main()





