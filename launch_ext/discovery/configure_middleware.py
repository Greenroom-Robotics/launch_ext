from launch.actions import SetLaunchConfiguration

from launch_ext.actions import ConfigureFastDDS, ConfigureZenoh, ConfigureFastDDSEasyMode
from launch_ext.actions.configure_zenoh import deep_merge
from launch_ext.discovery.discovery_config import Discovery


def configure_middleware(discovery: Discovery, with_server=True):
    if discovery.type == "zenoh":
        zenoh = discovery.zenoh
        router_peers = zenoh.router_peers
        router_config = zenoh.router_config
        session_config = zenoh.session_config

        # Merge router_peers into router_config connect/endpoints
        if router_peers:
            peer_endpoints = [f"tcp/{peer}:7447" for peer in router_peers]
            router_config = deep_merge(
                router_config,
                {"connect": {"endpoints": peer_endpoints}},
            )

        return [
            SetLaunchConfiguration("fastdds_profile_super_client", ""),
            ConfigureZenoh(
                with_router=zenoh.with_router and with_server,
                router_config=router_config,
                session_config=session_config,
                generate_router_config_file=True,
                generate_session_config_file=True,
            ),
        ]

    if discovery.type == "fastdds":
        fastdds = discovery.fastdds
        return [
            ConfigureFastDDS(
                with_discovery_server=fastdds.with_discovery_server and with_server,
                discovery_server_ip=fastdds.discovery_server_ip,
                allowed_interfaces=fastdds.allowed_interfaces,
                simple_discovery=False,
            ),
        ]

    if discovery.type == "easy":
        return [
            ConfigureFastDDSEasyMode(
                easy_mode_base_address=discovery.easy.base_address,
            ),
        ]

    return [
        ConfigureFastDDS(
            with_discovery_server=False,
            discovery_server_ip="0.0.0.0",
            allowed_interfaces=[],
            simple_discovery=True,
        ),
    ]
