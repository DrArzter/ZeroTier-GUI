import asyncio
from zerotier_gui.api import (
    get_my_id,
    get_networks,
    get_network_members,
    get_network_member,
    get_network_by_id,
)

async def main():

    
    network = await get_network_by_id("9e1948db6327faad")
    if "config" in network and "name" in network["config"]:
        print(network["config"]["name"])
        print(len(network["config"]["name"]))

if __name__ == "__main__":
    asyncio.run(main())