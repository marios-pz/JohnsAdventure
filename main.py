"""
    Welcome to John's Adventure! Hope you like my new game!

    Please be patient with some pieces of the code,
    it will take some time to clean the code ;')

"""

from data.scripts.world import GameManager

import asyncio


async def main(debug=False, first_state="player_room", no_rect=False):
    while 1:
        gm = GameManager(debug=debug, first_state=first_state, no_rect=no_rect)

        gm.update()
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
