import gui
import api

import asyncio


async def main():

    networks = await api.get_networks()
    members = await api.get_network_members(networks[0]["id"])


if __name__ == "__main__":
    asyncio.run(main())
