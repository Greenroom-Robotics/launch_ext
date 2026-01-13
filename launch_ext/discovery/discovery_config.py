from typing import Literal
from pydantic import BaseModel
from pydantic.fields import Field


class DiscoverySimple(BaseModel):
    type: Literal["simple"] = "simple"
    ros_domain_id: int = Field(
        default=0,
        description="ROS domain ID",
    )
    own_ip: str = Field(
        default="0.0.0.0",
        description="IP/host/interface address of the primary network interface. This is where DDS traffic will route to.",
    )
    discovery_range: Literal["subnet", "localhost"] = Field(
        default="localhost",
        description="Discovery range: 'localhost' sets ROS_AUTOMATIC_DISCOVERY_RANGE to LOCALHOST, 'subnet' sets it to SUBNET.",
    )


class DiscoveryFastDDS(BaseModel):
    type: Literal["fastdds"] = "fastdds"
    with_discovery_server: bool = Field(
        default=True,
        description="Run the discovery server. It will bind to 0.0.0.0:11811",
    )
    discovery_server_ip: str = Field(
        default="0.0.0.0",
        description="IP/host/interface of the discovery server. Assumes port of 11811",
    )
    own_ip: str = Field(
        default="0.0.0.0",
        description="IP/host/interface address of the primary network interface. This is where DDS traffic will route to.",
    )


class DiscoveryZenoh(BaseModel):
    type: Literal["zenoh"] = "zenoh"
    with_discovery_server: bool = Field(default=True, description="Run the zenoh router")
    discovery_server_ip: str = Field(
        default="0.0.0.0",
        description="IP/host/interface of the discovery server.",
    )


class DiscoveryEasy(BaseModel):
    type: Literal["easy"] = "easy"
    base_address: str = Field(
        default="127.0.0.1",
        description="Base address for easy discovery",
    )
    ros_domain_id: int = Field(
        default=0,
        description="ROS domain ID",
    )


Discovery = DiscoveryZenoh | DiscoveryFastDDS | DiscoverySimple | DiscoveryEasy


def discovery_field() -> Field:
    return Field(
        default_factory=lambda: DiscoverySimple(),
        discriminator="type",
        description="Middleware discovery configuration",
    )
