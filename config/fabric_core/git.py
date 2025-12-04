"""
This file contains functions to connect and manage Github connections to Fabric workspaces
"""
from .utils import call_azure_fabric_rest_api, load_local_env_file
import json
import os


load_local_env_file()


def get_or_create_git_connection(git_config: dict) -> str|None:
    """
    This function creates a connection to Github for Fabric.
    """
    owner_name = git_config.get("organization")
    repo_name = git_config.get("repository")
    connection_name = f"GitHub-{owner_name}-{repo_name}"

    list_response = call_azure_fabric_rest_api(api_endpoint="connections")
    list_json = json.loads(list_response.stdout)

    if list_json.get("status_code") == 200:
        connections = list_json.get("text", {}).get("value", [])
        for conn in connections:
            if conn.get("displayName") == connection_name:
                print(f"✓ Using existing connection: {connection_name}")
                return conn.get("id")

    github_url = f"https://github.com/{owner_name}/{repo_name}"
    request_body = {
        "connectivityType": "ShareableCloud",
        "displayName": connection_name,
        "connectionDetails": {
            "type": "GitHubSourceControl",
            "creationMethod": "GitHubSourceControl.Contents",
            "parameters": [{"dataType": "Text", "name": "url", "value": github_url}]
        },
        "credentialDetails": {
            "credentials": {"credentialType": "Key", "key": os.getenv("GITHUB_PAT")}
        }
    }

    create_response = call_azure_fabric_rest_api(api_endpoint="connections", method="post", request_body=request_body)
    create_json = json.loads(create_response.stdout)

    if create_json.get("status_code") in [200, 201]:
        connection_id = create_json.get("text", {}).get("id")
        print(f"✓ Created connection: {connection_name}")
        return connection_id

    return None


def connect_workspace_to_git(workspace_id:str, workspace_name:str, directory_name:str, git_config:dict, connection_id:str)->bool:
    """
    This function connects a workspace to Github repo.
    """
    request_body = {
        "gitProviderDetails": {
            "ownerName": git_config.get("organization"),
            "gitProviderType": git_config.get("provider"),
            "repositoryName": git_config.get("repository"),
            "branchName": git_config.get("branch"),
            "directoryName": directory_name
        },
        "myGitCredentials": {
            "source": "ConfiguredConnection",
            "connectionId": connection_id
        }
    }

    connect_response = call_azure_fabric_rest_api(api_endpoint=f"workspaces/{workspace_id}/git/connect",
                                    method="post", request_body=request_body)
    connect_json = json.loads(connect_response.stdout)

    if connect_json.get("status_code") in [200, 201]:
        print(f"✓ Connected {workspace_name} to Git: {directory_name}")
        return True
    
    return False


