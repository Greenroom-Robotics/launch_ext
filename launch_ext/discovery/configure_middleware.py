from launch.actions import SetLaunchConfiguration

from launch_ext.actions import ConfigureFastDDS, ConfigureZenoh

def configure_middleware(config):
    if config.discovery.type == "zenoh":
        return [
            SetLaunchConfiguration("fastdds_profile_super_client", ""),
            ConfigureZenoh(
                with_router=config.discovery.with_discovery_server,
                router_config={
                    "connect": {
                        "endpoints": [f"tcp/{config.discovery.discovery_server_ip}:7447"]
                    },
                    "listen": {"endpoints": ["tcp/0.0.0.0:7447"]},
                },
                session_config={},
            ),
        ]
    if config.discovery.type == "fastdds":
        return [
            ConfigureFastDDS(
                discovery_server_address="0.0.0.0",
                with_discovery_server=config.discovery.with_discovery_server,
                discovery_server_ip=config.discovery.discovery_server_ip,
                own_ip=config.discovery.own_ip,
                simple_discovery=False,
            ),
        ]
    return [
        ConfigureFastDDS(
            discovery_server_address="0.0.0.0",
            with_discovery_server=False,
            discovery_server_ip="0.0.0.0",
            own_ip="0.0.0.0",
            simple_discovery=True,
        ),
    ]
