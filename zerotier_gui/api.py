import json
import aiohttp
import asyncio
import os
from .decorators import async_logging, handle_exceptions
from .utils import state, run_command, create_and_run_temp_script

# Headers for API requests
headers = {
    "Authorization": f"Bearer {os.environ.get('ZEROTIER_API_TOKEN', 'Ikzh5eOZrZLFeyvgPQu1MEMpMudGLIUz')}"
}

@async_logging
@handle_exceptions
async def get_my_id():
    """Get the ID of the current ZeroTier node."""
    # If ID is already saved in state, return it
    if state.my_id:
        return state.my_id
        
    # Otherwise get ID via zerotier-cli
    stdout, _, returncode = await run_command(["zerotier-cli", "info"])
    
    if returncode == 0:
        # Parse output to get ID
        # Example output: "200 info 23596334a0 1.14.2 ONLINE"
        parts = stdout.strip().split()
        if len(parts) >= 3 and parts[0] == "200":
            state.my_id = parts[2]
            return state.my_id
    
    return None


@async_logging
@handle_exceptions
async def join_network(network_id: str):
    """Join a ZeroTier network with the given ID."""
    _, _, returncode = await run_command(["zerotier-cli", "join", network_id], check=False)
    return returncode == 0


@async_logging
@handle_exceptions
async def leave_network(network_id: str):
    """Leave a ZeroTier network with the given ID."""
    _, _, returncode = await run_command(["zerotier-cli", "leave", network_id], check=False)
    return returncode == 0


@async_logging
@handle_exceptions
async def update_user_record(data):
    """Update the user record in the ZeroTier API."""
    async with aiohttp.ClientSession() as session:
        async with session.put(
            "https://api.zerotier.com/api/v1/user",
            headers={"Content-Type": "application/json", **headers},
            json=json.dumps(data),
        ) as response:
            return await response.json()


@async_logging
@handle_exceptions
async def get_networks():
    """Get all networks from the ZeroTier API."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.zerotier.com/api/v1/network", headers=headers
        ) as response:
            return await response.json()


@async_logging
@handle_exceptions
async def get_network_by_id(network_id: str):
    """Get information about a network by its ID via the ZeroTier API."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.zerotier.com/api/v1/network/{network_id}", headers=headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                return None


@async_logging
@handle_exceptions
async def create_network():
    """Create a new ZeroTier network."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.zerotier.com/api/v1/network",
            headers={"Content-Type": "application/json", **headers},
            json={},
        ) as response:
            return await response.json()


@async_logging
@handle_exceptions
async def delete_network(network_id: str):
    """Delete a ZeroTier network with the given ID."""
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"https://api.zerotier.com/api/v1/network/{network_id}", headers=headers
        ) as response:
            return await response.json()


@async_logging
@handle_exceptions
async def get_network_members(network_id: str):
    """Get all members of a ZeroTier network with the given ID."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.zerotier.com/api/v1/network/{network_id}/member",
            headers=headers,
        ) as response:
            return await response.json()


@async_logging
@handle_exceptions
async def get_network_member(network_id: str, member_id: str):
    """Get information about a specific member of a ZeroTier network."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.zerotier.com/api/v1/network/{network_id}/member/{member_id}",
            headers=headers,
        ) as response:
            return await response.json()


@async_logging
@handle_exceptions
async def delete_network_member(network_id: str, member_id: str):
    """Delete a member from a ZeroTier network."""
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"https://api.zerotier.com/api/v1/network/{network_id}/member/{member_id}",
            headers=headers,
        ) as response:
            return await response.json()


def hide_physical_address(member: dict):
    """Hide the physical address of a member for privacy."""
    member["physicalAddress"] = "hidden"
    return member


@async_logging
@handle_exceptions
async def ping_member(member: dict):
    """Ping a ZeroTier network member."""
    stdout, _, _ = await run_command(
        ["ping", "-c", "1", member["config"]["ipAssignments"][0]], 
        check=False
    )
    return stdout


@async_logging
@handle_exceptions
async def set_station_name(name: str, network_id: str):
    """Set the station name in a ZeroTier network.
    
    Note: This function uses ZeroTier's internal API, as
    zerotier-cli does not directly support setting the station name.
    """
    script_content = f"""#!/bin/bash
# Script to set station name in ZeroTier
NETWORK_ID="{network_id}"
NAME="{name}"
CONFIG_FILE="/var/lib/zerotier-one/networks.d/$NETWORK_ID.conf"

# Check if the configuration file exists
if [ -f "$CONFIG_FILE" ]; then
    # Create a temporary file
    TMP_FILE=$(mktemp)
    
    # Read current configuration
    cat "$CONFIG_FILE" > "$TMP_FILE"
    
    # Update or add the name field
    if grep -q '"name"' "$TMP_FILE"; then
        # Replace existing name
        sed -i 's/"name"[[:space:]]*:[[:space:]]*"[^"]*"/"name": "'"$NAME"'"/' "$TMP_FILE"
    else
        # Add new name field
        sed -i 's/{{/{{ "name": "'"$NAME"'",/' "$TMP_FILE"
    fi
    
    # Copy back
    cat "$TMP_FILE" > "$CONFIG_FILE"
    
    # Remove temporary file
    rm "$TMP_FILE"
    
    # Restart service
    systemctl restart zerotier-one
    
    echo "Station name set to: $NAME"
    exit 0
else
    echo "Network configuration file not found"
    exit 1
fi
"""
    
    stdout, stderr, returncode = await create_and_run_temp_script(script_content, use_sudo=True)
    
    if returncode == 0:
        return True
    else:
        print(f"Error setting station name: {stderr}")
        return False


@async_logging
@handle_exceptions
async def is_member_of_network(network_id: str):
    """Check if the current device is a member of the specified network."""
    # Check if the device ID is in state
    if not state.my_id:
        await get_my_id()
        if not state.my_id:
            return False
    
    # Get the list of network members
    members = await get_network_members(network_id)
    
    if not members:
        return False
    
    # Check if our device is in the list of members
    for member in members:
        if member.get("nodeId") == state.my_id:
            # Check that the device is authorized
            return member.get("authorized", False)
    
    return False


@async_logging
@handle_exceptions
async def get_current_user():
    """Get information about the current user via the ZeroTier API."""
    # If user data is already saved in state, return it
    if state.user_id and state.user_data:
        return state.user_data
        
    # Otherwise get data via API
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.zerotier.com/api/v1/status", headers=headers
        ) as response:
            data = await response.json()
            
            if isinstance(data, dict) and "user" in data and isinstance(data["user"], dict):
                # Save user data
                state.user_data = data
                state.user_id = data["user"]["id"]
                
            return data


@async_logging
@handle_exceptions
async def initialize_user():
    """Initialize user data when starting the application."""
    # Get device ID
    await get_my_id()
    
    # Get user data
    user_data = await get_current_user()
    
    # Check that data was received successfully
    if not user_data or not isinstance(user_data, dict) or "user" not in user_data:
        return False
        
    return True


@async_logging
@handle_exceptions
async def is_network_owner(network_id: str):
    """Check if the current user is the creator/owner of the specified network."""
    # Check if the user ID is in state
    if not state.user_id:
        # If not, get user data
        await get_current_user()
        if not state.user_id:
            return False
    
    # Get information about the network
    network = await get_network_by_id(network_id)
    
    if not network or not isinstance(network, dict):
        return False
        
    # Check if the user ID matches the network owner ID
    owner_id = network.get("ownerId")
    
    if not owner_id:
        return False
    
    # Return the result of the comparison
    return owner_id == state.user_id
