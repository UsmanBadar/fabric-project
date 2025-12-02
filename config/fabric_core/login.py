"""
Method to login to Azure using Service Principal
"""
from .utils import run_fabric_cli_command, load_local_env_file
import os


load_local_env_file()

client_id = os.getenv("SPN_CLIENT_ID")
client_secret = os.getenv("SPN_CLIENT_SECRET")
tenant_id = os.getenv("AZURE_TENANT_ID")


def login():
    try:
        result = run_fabric_cli_command(["auth", "login", "-u", f"{client_id}", "-p", f"{client_secret}", "--tenant", f"{tenant_id}"])
        if result.returncode == 0:
            print(f"Successfully logged In. return code: {result.returncode}")
        else:
            print(f"Login Failed. return code: {result.returncode}\n, stdout: {result.stdout}\n, stderr: {result.stderr}")
    except Exception as e:
        print(f"Failed to run login function. {e}")


