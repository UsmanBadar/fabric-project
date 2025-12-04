"""
This file contains functions for creating and managing workspaces in Fabric.
"""
from .utils import run_fabric_cli_command, call_azure_fabric_rest_api
import re
import time
import json
from typing import Sequence

def workspace_exists(workspace_name: str)-> bool:
    """Check if a Fabric workspace exists."""
    return run_fabric_cli_command(['ls', f'{workspace_name}.Workspace']).returncode == 0


def get_workspace_id(workspace_name)-> str|None:
    """Get the UUID of a workspace by name."""
    response = run_fabric_cli_command(
        ['get', f'{workspace_name}.Workspace', '-q', 'id'])
    if response.returncode == 0:
        workspace_id = response.stdout.strip()
        if workspace_id:
            return workspace_id
    uuid_match = re.search(
        r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', response.stdout.lower())
    return uuid_match.group() if uuid_match else None


def create_workspace(workspace_config: dict)->str:
    """
    Function to create Fabric workspaces
    """
    workspace_name = workspace_config['name']

    if workspace_exists(workspace_name):
        print(f"✓ {workspace_name} exists")
        return get_workspace_id(workspace_name)

    run_fabric_cli_command(['create',
                f'{workspace_name}.Workspace', '-P', f'capacityname={workspace_config["capacity"]}'])
    print(f"✓ Created {workspace_name}")

    time.sleep(5)
    return get_workspace_id(workspace_name)


def assign_permissions(workspace_id: str, permissions: Sequence[dict], security_groups: dict)->None:
    """
    Function to assign workspace role and user permissions
    """
    for permission in permissions:
        group_id = security_groups.get(permission.get('group'))

        request_body = {
            "principal": {
                "id": group_id,
                "type": "Group",
                "groupDetails": {"groupType": "SecurityGroup"}
            },
            "role": permission.get('role')
        }

        assign_response = call_azure_fabric_rest_api(api_endpoint=f'workspaces/{workspace_id}/roleAssignments', method="post", 
                                                      request_body=request_body)
        response_json = json.loads(assign_response.stdout)

        if response_json.get('status_code') in [200, 201]:
            print(
                f"  ✓ Assigned {permission['role']} to {permission['group']}")

