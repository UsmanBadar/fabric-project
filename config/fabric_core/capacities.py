"""
Functions related to creating and managing Fabric capacities.
"""

import os
import json
import time

from .utils import call_azure_fabric_rest_api, load_local_env_file

load_local_env_file()

subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")


def check_capacity_exists(capacity_name: str, resource_group: str) -> bool:
    """Check if a Fabric capacity exists in Azure."""
    response = call_azure_fabric_rest_api(
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/"
        f"Microsoft.Fabric/capacities/{capacity_name}?api-version=2023-11-01",
        audience="azure",
    )
    result = json.loads(response.stdout or "{}")
    return result.get("status_code", 0) == 200


def get_capacity_status(capacity_name: str, resource_group: str) -> tuple[str | None, str | None]:
    """
    Return (provisioning_state, state) from ARM.

    Raises if the ARM call does not return 200.
    """
    response = call_azure_fabric_rest_api(
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/"
        f"Microsoft.Fabric/capacities/{capacity_name}?api-version=2023-11-01",
        audience="azure",
    )
    result = json.loads(response.stdout or "{}")
    status_code = result.get("status_code", 0)

    if status_code != 200:
        raise RuntimeError(f"Failed to fetch capacity status: {result}")

    text = result.get("text", {}) or {}
    props = text.get("properties", {}) or {}

    provisioning_state = props.get("provisioningState")
    state = props.get("state")

    return provisioning_state, state


def wait_for_capacity_ready(
    capacity_name: str,
    resource_group: str,
    max_wait_seconds: int = 600,
    poll_seconds: int = 15,
) -> bool:
    """
    Poll until capacity is ready.
    Ready means provisioningState == 'Succeeded' and if state exists, state is 'Active' or 'Paused'.
    Returns True if ready, False otherwise.
    """
    waited = 0
    while waited < max_wait_seconds:
        prov_state, state = get_capacity_status(capacity_name, resource_group)

        if prov_state == "Succeeded":
            if state in ["Active", "Paused"]:
                print(f"✓ {capacity_name} is ready (provisioningState={prov_state}, state={state})")
                return True

        print(f"... waiting for {capacity_name} (provisioningState={prov_state}, state={state})")
        time.sleep(poll_seconds)
        waited += poll_seconds

    print(f"✗ {capacity_name} not ready after {max_wait_seconds} seconds")
    return False


def create_capacity(capacity_config: dict, resource_group: str, defaults: dict) -> None:
    """
    Create a Fabric capacity if it does not already exist.
    """
    capacity_name = capacity_config["name"]

    if check_capacity_exists(capacity_name, resource_group):
        print(f"✓ {capacity_name} exists")
        return

    admin_members = capacity_config.get("admin_members", defaults.get("capacity_admins", ""))
    admin_members = admin_members if isinstance(admin_members, list) else [
        admin_id.strip()
        for admin_id in admin_members.split(",")
        if admin_id.strip()
    ]

    request_body = {
        "location": capacity_config.get("region", defaults.get("region")),
        "sku": {"name": capacity_config.get("sku", defaults.get("sku")), "tier": "Fabric"},
        "properties": {"administration": {"members": admin_members}},
    }

    response = call_azure_fabric_rest_api(
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/"
        f"Microsoft.Fabric/capacities/{capacity_name}?api-version=2023-11-01",
        method="put",
        request_body=request_body,
        audience="azure",
    )
    result = json.loads(response.stdout or "{}")
    status_code = result.get("status_code", 0)

    if status_code in [200, 201]:
        print(f"✓ Created {capacity_name}")
        wait_for_capacity_ready(capacity_name, resource_group)
    else:
        raise RuntimeError(f"Failed to create capacity {capacity_name}: {result}")


def suspend_capacity(capacity_name: str, resource_group: str) -> bool:
    """Suspend a Fabric capacity to stop billing."""
    for _ in range(5):
        response = call_azure_fabric_rest_api(
            f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/"
            f"Microsoft.Fabric/capacities/{capacity_name}/suspend?api-version=2023-11-01",
            method="post",
            audience="azure",
        )
        result = json.loads(response.stdout or "{}")
        status_code = result.get("status_code", 0)
        if status_code in [200, 202]:
            print(f"✓ Suspended {capacity_name}")
            return True
        time.sleep(60)

    print(f"✗ Failed to suspend {capacity_name}")
    return False
