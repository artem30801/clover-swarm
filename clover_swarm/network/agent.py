import logging
import sys
import uuid

import trio
import zmq
import zmq.asyncio
from network.beacon import Beacon
from network.utils import get_ip

import clover_swarm.containers as containers

# from clover_swarm import error

# from clover_swarm.containers import AgentContainer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


# class ConnectedPeer:
#     expires_at = None
#
#     def __init__(self, uuid):
#         self.addr = None
#         self.uuid = uuid
#         self.heartbeat = None
#         self.dealer = None
#
#     def is_alive(self):
#         """
#         Resets the peers expiry time
#         """
#         self.expires_at = time.time() + 5


class Agent:
    def __init__(self, port: int = None, name: str = None, beacon=Beacon, ctx=None):

        self.port = port
        self.host = None
        self.uuid = uuid.uuid4()
        self.name = name or self.uuid.hex[:8]

        self.running = False
        self.start_stop_lock = trio.Lock()

        self.ctx = ctx or zmq.Context.instance()
        self.beacon = beacon(self)
        # self.router =
        self.peers = {}

    def __str__(self):
        return f"<Agent (name: {self.name}; uuid: {self.uuid}>"

    def __hash__(self):
        return hash(self.uuid)

    async def start(self):
        async with self.start_stop_lock:
            if self.running:
                raise RuntimeError("Agent already running")
            logger.debug(f"Starting {self}")

            self.host = await get_ip()
            await self.beacon.start()

            logger.info(f"Started {self}")

    async def stop(self):
        logger.debug(f"Stopping {self}")

        logger.info(f"Stopped {self}")

    async def start_beacon(self):
        logger.debug(f"Starting beacon of {self}")

    async def stop_beacon(self):
        logger.debug(f"Stopping beacon of {self}")


if __name__ == "__main__":
    container = containers.AgentContainer()
    container.wire(modules=[sys.modules[__name__]])

    agent = container.agent()
    trio.run(agent.start)
