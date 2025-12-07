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


def update_workspace_from_git(workspace_id, workspace_name):
    """
    Update workspace content from Git (pull from Git).

    This syncs the Git repository content into the workspace.
    """
    # Get Git status to retrieve remoteCommitHash
    status_response = call_azure_fabric_rest_api(api_endpoint=f'workspaces/{workspace_id}/git/status')

    if not status_response.stdout.strip():
        print(f"  ⚠ Failed to get Git status")
        return False

    try:
        status_json = json.loads(status_response.stdout)
        status_code = status_json.get('status_code')

        # Handle uninitialized connection
        if status_code == 400:
            error_text = status_json.get('text', {})
            if error_text.get('errorCode') == 'WorkspaceGitConnectionNotInitialized':
                print(f"  → Initializing Git connection")
                call_azure_fabric_rest_api(api_endpoint=f'workspaces/{workspace_id}/git/initializeConnection', method="post")
                # Retry getting status after initialization
                status_response = call_azure_fabric_rest_api(api_endpoint=f'workspaces/{workspace_id}/git/status')
                status_json = json.loads(status_response.stdout)
                status_code = status_json.get('status_code')

        if status_code != 200:
            error_text = status_json.get('text', {})
            print(f"  ⚠ Failed to get Git status: {status_code}")
            print(f"     Error: {error_text}")
            return False

        remote_commit_hash = status_json.get('text', {}).get('remoteCommitHash')
        if not remote_commit_hash:
            print(f"  ⚠ No remoteCommitHash found in status")
            return False
    except json.JSONDecodeError:
        print(f"  ⚠ Failed to parse Git status")
        return False

    # Update from Git using the remoteCommitHash
    update_request = {
        "remoteCommitHash": remote_commit_hash,
        "conflictResolution": {
            "conflictResolutionType": "Workspace",
            "conflictResolutionPolicy": "PreferWorkspace"
        },
        "options": {"allowOverrideItems": True}
    }

    update_response = call_azure_fabric_rest_api(api_endpoint=f'workspaces/{workspace_id}/git/updateFromGit', method="post",
        request_body=update_request)

    if not update_response.stdout.strip():
        return True  # Empty response is acceptable

    try:
        response_json = json.loads(update_response.stdout)
        if response_json.get('status_code') in [200, 201, 202]:
            print(f"  ✓ Updated {workspace_name} from Git")
            return True
    except json.JSONDecodeError:
        pass

    print(f"  ⚠ Update from Git may have failed")
    return False



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


