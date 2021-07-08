# import logging
# import sys

import network.agent as agent_module
import network.beacon as beacon_module
from dependency_injector import containers, providers
from dynaconf import Dynaconf, Validator


class AgentContainer(containers.DeclarativeContainer):
    # config1 = providers.Configuration(
    #     default={
    #         "beacon": {
    #             "send": True,
    #             "listen": True,
    #             "port": 19700,
    #             "broadcast": "255.255.255.255",
    #             "send_interval": 1,
    #         },
    #         "agent": {
    #             "port": 19701,
    #         },
    #     }
    # )

    config = providers.Object(
        Dynaconf(
            settings_files=["config.toml"],
            validators=[
                # beacon
                Validator("beacon.send", "beacon.listen", default=True, is_type_of=bool),
                Validator("beacon.port", default=19700, is_type_of=int, gt=0, lte=65535),
                Validator("beacon.broadcast", default="255.255.255.255", is_type_of=str),
                Validator("beacon.send_interval", default=1, is_type_of=(float, int), gt=0),
                # agent
                Validator("agent.port", default=19701, is_type_of=int, gt=0, lte=65535),
            ],
        )
    )

    # logging = providers.Resource(
    #     logging.basicConfig,
    #     stream=sys.stdout,
    #     level=config.log.level,
    #     format=config.log.format,
    # )

    beacon = providers.Factory(
        beacon_module.Beacon,
        port=config().beacon.port,
        broadcast=config().beacon.broadcast,
        send_interval=config().beacon.send_interval,
    )

    agent = providers.Factory(
        agent_module.Agent,
        port=config().agent.port,
        beacon=beacon.provider,
    )
