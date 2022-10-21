"""
    Welcome to John's Adventure! Hope you like my new game!

    Please be patient with some pieces of the code,
    it will take some time to clean the code ;')

"""

from data.scripts.world import GameManager

import asyncio
import sys

flags = sys.argv


def main(
    debug: bool = False,
    first_state: str = "player_room",
    no_rect: bool = True,
):
    gm = GameManager(debug=debug, first_state=first_state, no_rect=no_rect)
    asyncio.run(gm.update())


if __name__ == "__main__":
    if len(flags) > 1:
        main(debug=True, first_state=flags[1], no_rect=True)
    else:
        main()
