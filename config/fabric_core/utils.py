"""
Helper functions for interacting with Microsoft Fabric using the Fabric CLI.
"""

import sys, shutil, json, subprocess
from pathlib import Path



def set_stdout_encoding_to_utf_8() -> None:
    """
    Sets the standard output encoding to UTF 8.
    """
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')


def get_fab_cli_executable_path() -> str:
    """
    Returns the path to the Fabric CLI executable.
    Automatically resolves virtual environment and system installations on macOS.
    """
    # Virtual environment active
    if sys.prefix != sys.base_prefix:
        fab_path = Path(sys.prefix) / "bin" / "fab"
        if fab_path.exists():
            return str(fab_path)

    # Fallback to system PATH
    return shutil.which("fab") or "fab"


def run_fabric_cli_command(cmd: list[str]) -> subprocess.CompletedProcess:
    """
    Runs a command in a separate process and returns the completed process object
    """
    full_cmd = [get_fab_cli_executable_path(), *cmd]
    return subprocess.run(full_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def call_azure_fabric_rest_api(api_endpoint: str, method: str = "get", 
                         request_body: dict|None = None, audience: str|None = None, 
                         params: dict|None = None) -> subprocess.CompletedProcess:
    
    """
    Calls a Microsoft Azure and Fabric REST API endpoint through the Fabric CLI.
    Builds the CLI command dynamically using the provided HTTP method,
    request body, audience, and query parameters, then executes the request
    and returns the full process response.
    """
        
    cmd = [get_fab_cli_executable_path(), "api", api_endpoint, "-X", method]
    if request_body:
        cmd.extend(["-i", json.dumps(request_body)])
    if audience:
        cmd.extend(["-A", audience])
    if params:
        for key, value in params.items():
            cmd.extend(["-P", f"{key}={value}"])
    result = run_fabric_cli_command(cmd)
    return result






