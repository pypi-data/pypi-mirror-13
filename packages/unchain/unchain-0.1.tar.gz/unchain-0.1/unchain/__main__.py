# Unchain your HTTP backend with authenticated WebSockets.
# (c) 2015 Hugo Herter

"""
Start a daemon using an AsyncIO event loop.
"""

import asyncio
from unchain import init

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
