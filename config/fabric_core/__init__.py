"""
Fabric Core - Reusable modules for Microsoft Fabric CLI operations.
"""

from .utils import *
from .login import login
from .load_config import load_config_from_file
from .capacities import (check_capacity_exists, get_capacity_status, 
                         wait_for_capacity_ready, create_capacity, suspend_capacity)
from .workspaces import (get_workspace_id, workspace_exists, create_workspace, assign_permissions)

from .git_integration import (get_or_create_git_connection, update_workspace_from_git, connect_workspace_to_git)

__all__ = [
    "load_local_env_file",
    "set_stdout_encoding_to_utf_8",
    "get_fab_cli_executable_path",
    "run_fabric_cli_command",
    "call_azure_fabric_rest_api",
    "login",
    "load_config_from_file",
    "check_capacity_exists",
    "get_capacity_status",
    "wait_for_capacity_ready",
    "create_capacity", 
    "suspend_capacity",
    "get_workspace_id", 
    "workspace_exists", 
    "create_workspace", 
    "assign_permissions",
    "get_or_create_git_connection", 
    "update_workspace_from_git", 
    "connect_workspace_to_git"
]