import asyncio
from zerotier_gui.api import (
    get_my_id,
    get_networks,
    get_network_members,
    get_network_member,
    get_network_by_id,
)


async def main():
    me = "23596334a0"
    print(me)

    networks = await get_networks()
    #print(networks)
    
    network = get_network_by_id(networks[0]['id'])
    print(network)
    
    user = await get_network_member(networks[0]['id'], me)
    print(user)

if __name__ == "__main__":
    asyncio.run(main())