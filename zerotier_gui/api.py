import json
import aiohttp
import asyncio
import subprocess
from .decorators import async_logging, handle_exceptions
from .utils import state

headers = {
    "Authorization": "Bearer Ikzh5eOZrZLFeyvgPQu1MEMpMudGLIUz",
}


@async_logging
@handle_exceptions
async def get_my_id():
    process = await asyncio.create_subprocess_exec(
        "zerotier-cli",
        "info",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    my_id = stdout.decode("utf-8").split()[2]
    state.my_id = my_id  # Сохраняем ID
    return my_id


@async_logging
@handle_exceptions
async def update_user_record(data):
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
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.zerotier.com/api/v1/network", headers=headers
        ) as response:
            return await response.json()


@async_logging
@handle_exceptions
async def get_network_by_id(network_id: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.zerotier.com/api/v1/network/{network_id}",
            headers=headers
        ) as response:
            return await response.json()


@async_logging
@handle_exceptions
async def create_network():
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
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"https://api.zerotier.com/api/v1/network/{network_id}", headers=headers
        ) as response:
            return await response.json()


@async_logging
@handle_exceptions
async def get_network_members(network_id: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.zerotier.com/api/v1/network/{network_id}/member",
            headers=headers,
        ) as response:
            return await response.json()


@async_logging
@handle_exceptions
async def get_network_member(network_id: str, member_id: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.zerotier.com/api/v1/network/{network_id}/member/{member_id}",
            headers=headers,
        ) as response:
            return await response.json()


@async_logging
@handle_exceptions
async def delete_network_member(network_id: str, member_id: str):
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"https://api.zerotier.com/api/v1/network/{network_id}/member/{member_id}",
            headers=headers,
        ) as response:
            return await response.json()


def hide_physical_address(member: dict):
    member["physicalAddress"] = "hidden"
    return member


@async_logging
@handle_exceptions
async def ping_member(member: dict):
    process = await asyncio.create_subprocess_exec(
        "ping",
        "-c",
        "1",
        member["config"]["ipAssignments"][0],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    return stdout.decode()


@async_logging
@handle_exceptions
async def join_network(network_id: str):
    process = await asyncio.create_subprocess_exec(
        "zerotier-cli",
        "join",
        network_id,
    )
    await process.wait()
    return process.returncode == 0
