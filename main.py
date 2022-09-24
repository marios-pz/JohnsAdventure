"""
    Welcome to John's Adventure! Hope you like my new game!

    Please be patient with some pieces of the code,
    it will take some time to clean the code ;')

"""

from data.scripts.world import main

import asyncio


async def amain():

    game_instance = main()
    game_instance.update()

    await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(amain())
