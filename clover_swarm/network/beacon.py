import functools
import logging
import socket
import struct
import typing
import uuid

import trio
import trio_util
from dependency_injector.wiring import Provide, inject, provided

logger = logging.getLogger(__name__)


class Beacon:
    beacon_version = 1
    prefix = b"CS"  # Clever Swarm
    struct_format = ">2sh16sH"  # 2 identifier bytes, 16 UUID bytes, unsigned short (port)
    message_len = 32
    socket = None

    sender: typing.Optional[trio.CancelScope] = None
    listener: typing.Optional[trio.CancelScope] = None

    #    @inject
    def __init__(
        self,
        agent,
        port: int = 19700,
        broadcast: str = "255.255.255.255",
        send_interval: int = 5,
    ):
        self.agent = agent

        self.port = port
        self.broadcast = broadcast
        self.send_interval = send_interval

        self.running = False
        self.start_stop_lock = trio.Lock()

    def __str__(self):
        return f"{self.agent}'s beacon"

    @functools.cached_property
    def encode_message(self) -> bytes:
        packed = struct.pack(
            self.struct_format,
            self.prefix,
            self.beacon_version,
            self.agent.uuid.bytes,
            self.agent.port,
        )
        return packed

    def decode_message(self, message: bytes):
        prefix, version, peer_uuid, peer_port = struct.unpack(self.struct_format, message)
        return uuid.UUID(bytes=peer_uuid), peer_port

    @inject
    async def start(
        self,
        start_sender: bool = Provide["config", provided().beacon.send],
        start_listener: bool = Provide["config", provided().beacon.listen],
    ):
        if self.running:
            raise RuntimeError("Beacon already running")

        logger.debug(f"{self} starting on {self.broadcast}:{self.port}")

        self.socket = trio.socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        async with self.start_stop_lock, trio.open_nursery() as tasks:
            self.listener = None
            if start_listener:
                self.listener = await tasks.start(self._start_listener)

            self.sender = None
            if start_sender:
                self.sender = await tasks.start(self._start_sender)

        logger.debug(f"{self} tasks stopped")

    async def stop(self):
        logger.debug(f"Stopping beacon of {self}")

    async def _start_listener(self, task_status=trio.TASK_STATUS_IGNORED):
        logger.debug(f"Starting beacon listener of {self.agent}")
        await self.socket.bind(("", self.port))
        with trio.CancelScope() as scope:
            task_status.started(scope)
            logger.debug(f"Started beacon listener of {self.agent}")
            while True:
                await self._receive_beacon()

    async def _receive_beacon(self):
        message, (peer_host, _) = await self.socket.recvfrom(32)
        # print(peer_host, self.agent.host)
        if peer_host != self.agent.host:  # todo different strategy for local ip
            peer_uuid, peer_port = self.decode_message(message)
            if peer_uuid != self.agent.uuid:
                print(peer_uuid, peer_host, peer_port)

    async def _start_sender(self, task_status=trio.TASK_STATUS_IGNORED):
        logger.debug(f"{self} sender starting with interval {self.send_interval}")
        with trio.CancelScope() as scope:
            task_status.started(scope)
            async for _ in trio_util.periodic(self.send_interval):
                await self.socket.sendto(self.encode_message, (self.broadcast, self.port))
                logger.debug(f"{self} sent broadcast message")

    async def _send_beacon(self):
        self.socket.sendto(self.encode_message, (self.broadcast, self.port))
        logger.debug(f"{self.agent} beacon sent broadcast to {self.broadcast}:{self.port}")
