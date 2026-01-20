"""
Avahi D-Bus interface for managing mDNS/DNS-SD services.

This module provides a Python interface to Avahi's D-Bus API for
creating and managing service advertisements on the local network.

Docker Usage:
    To use from within a Docker container, mount D-Bus sockets:

    docker run:
        docker run -v /var/run/dbus:/var/run/dbus \
                   -v /var/run/avahi-daemon/socket:/var/run/avahi-daemon/socket \
                   your_image

    docker-compose:
        services:
          your_service:
            volumes:
              - /var/run/dbus:/var/run/dbus
              - /var/run/avahi-daemon/socket:/var/run/avahi-daemon/socket
            # Optional: simplest mDNS setup
            # network_mode: host

Example:
    from avahi_manager import AvahiService, AvahiServiceManager

    manager = AvahiServiceManager()
    manager.connect()

    service = AvahiService(
        name="My Robot",
        service_type="_ros2._tcp",
        port=11811,
        txt_records=["version=1.0"],
    )
    manager.create_service(service)
"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Literal, Optional

import dbus


class AvahiIfIndex(IntEnum):
    """Avahi interface index constants."""

    UNSPEC = -1  # Use all interfaces


class AvahiProtocol(IntEnum):
    """Avahi protocol constants."""

    UNSPEC = -1  # Use both IPv4 and IPv6
    INET = 0  # IPv4 only
    INET6 = 1  # IPv6 only


class AvahiPublishFlags(IntEnum):
    """Avahi publish flags."""

    NONE = 0
    UNIQUE = 1
    NO_PROBE = 2
    NO_ANNOUNCE = 4
    ALLOW_MULTIPLE = 8
    NO_REVERSE = 16
    NO_COOKIE = 32
    UPDATE = 64
    USE_WIDE_AREA = 128
    USE_MULTICAST = 256


class AvahiEntryGroupState(IntEnum):
    """Avahi entry group states."""

    UNCOMMITED = 0
    REGISTERING = 1
    ESTABLISHED = 2
    COLLISION = 3
    FAILURE = 4


@dataclass
class AvahiService:
    """Represents an Avahi service configuration."""

    name: str
    service_type: str
    port: int
    txt_records: list[str] = field(default_factory=list)
    domain: str = ""
    host: str = ""
    interface: int = AvahiIfIndex.UNSPEC
    protocol: int = AvahiProtocol.UNSPEC


class AvahiServiceManager:
    """
    Manages Avahi services via D-Bus.

    This class provides methods to create, commit, and remove
    mDNS/DNS-SD service advertisements through Avahi.
    """

    AVAHI_DBUS_NAME = "org.freedesktop.Avahi"
    AVAHI_DBUS_PATH_SERVER = "/"
    AVAHI_DBUS_INTERFACE_SERVER = "org.freedesktop.Avahi.Server"
    AVAHI_DBUS_INTERFACE_ENTRY_GROUP = "org.freedesktop.Avahi.EntryGroup"

    def __init__(self) -> None:
        """Initialize the Avahi service manager."""
        self._bus: Optional[dbus.SystemBus] = None
        self._server: Optional[dbus.Interface] = None
        self._entry_groups: dict[str, dbus.Interface] = {}

    def connect(self) -> None:
        """
        Connect to the Avahi daemon via D-Bus.

        Raises:
            dbus.DBusException: If connection to Avahi fails.
        """
        self._bus = dbus.SystemBus()
        server_obj = self._bus.get_object(self.AVAHI_DBUS_NAME, self.AVAHI_DBUS_PATH_SERVER)
        self._server = dbus.Interface(server_obj, self.AVAHI_DBUS_INTERFACE_SERVER)

    def disconnect(self) -> None:
        """Disconnect from D-Bus and free all entry groups."""
        for name in list(self._entry_groups.keys()):
            self.remove_service(name)
        self._entry_groups.clear()
        self._server = None
        self._bus = None

    def is_connected(self) -> bool:
        """Check if connected to Avahi daemon."""
        return self._server is not None

    def get_host_name(self) -> str:
        """
        Get the local hostname as configured in Avahi.

        Returns:
            The local hostname string.

        Raises:
            RuntimeError: If not connected to Avahi.
        """
        if not self._server:
            raise RuntimeError("Not connected to Avahi daemon")
        return str(self._server.GetHostName())

    def get_domain_name(self) -> str:
        """
        Get the local domain name.

        Returns:
            The local domain name (usually "local").

        Raises:
            RuntimeError: If not connected to Avahi.
        """
        if not self._server:
            raise RuntimeError("Not connected to Avahi daemon")
        return str(self._server.GetDomainName())

    def create_avahi_service(self, service: AvahiService) -> bool:
        """
        Create and register an Avahi service.

        Args:
            service: The service configuration to register.

        Returns:
            True if service was created successfully.

        Raises:
            RuntimeError: If not connected to Avahi.
            ValueError: If a service with the same name already exists.
            dbus.DBusException: If D-Bus operation fails.
        """
        if not self._server or not self._bus:
            raise RuntimeError("Not connected to Avahi daemon")

        if service.name in self._entry_groups:
            raise ValueError(f"Service '{service.name}' already exists")

        # Create a new entry group
        group_path = self._server.EntryGroupNew()
        group_obj = self._bus.get_object(self.AVAHI_DBUS_NAME, group_path)
        group = dbus.Interface(group_obj, self.AVAHI_DBUS_INTERFACE_ENTRY_GROUP)

        # Convert TXT records to the format Avahi expects (list of byte arrays)
        txt_array = [s.encode("utf-8") for s in service.txt_records]

        # Add the service to the entry group
        group.AddService(
            dbus.Int32(service.interface),
            dbus.Int32(service.protocol),
            dbus.UInt32(AvahiPublishFlags.NONE),
            service.name,
            service.service_type,
            service.domain,
            service.host,
            dbus.UInt16(service.port),
            txt_array,
        )

        # Commit the entry group to publish the service
        group.Commit()

        # Store the entry group for later management
        self._entry_groups[service.name] = group

        return True

    def remove_service(self, name: str) -> bool:
        """
        Remove a registered service.

        Args:
            name: The name of the service to remove.

        Returns:
            True if service was removed, False if service didn't exist.
        """
        if name not in self._entry_groups:
            return False

        group = self._entry_groups[name]
        try:
            group.Reset()
            group.Free()
        except dbus.DBusException:
            pass  # Group may already be freed

        del self._entry_groups[name]
        return True

    def list_services(self) -> list[str]:
        """
        List all registered service names.

        Returns:
            List of registered service names.
        """
        return list(self._entry_groups.keys())

    def get_service_state(self, name: str) -> Optional[AvahiEntryGroupState]:
        """
        Get the state of a registered service.

        Args:
            name: The name of the service.

        Returns:
            The entry group state, or None if service doesn't exist.
        """
        if name not in self._entry_groups:
            return None

        group = self._entry_groups[name]
        try:
            state = group.GetState()
            return AvahiEntryGroupState(state)
        except dbus.DBusException:
            return None

    def create_product_service(
        self,
        product: str,
        port: int = 80,
        protocol: Literal["http", "https"] = "http",
        path: str = "/",
        display_name: Optional[str] = None,
    ) -> bool:
        """
        Create and register a product service.

        Args:
            product: The product type to advertise.
            port: The port number the service is running on.
            protocol: The protocol ("http" or "https").
            path: The URL path to the service.
            display_name: Optional display name for the service. If None,
                uses the hostname from Avahi.

        Returns:
            True if service was created successfully.

        """
        hostname = self.get_host_name()
        vessel_name = display_name or ""
        service_type = f"_{product}._tcp"

        service = AvahiService(
            name=product,
            service_type=service_type,
            port=port,
            txt_records=[
                f"path={path}",
                f"protocol={protocol}",
                f"hostname={hostname}",
                f"vessel_name={vessel_name}",
                f"product={product}",
            ],
        )

        return self.create_avahi_service(service)

    def remove_product_service(self, product: str) -> bool:
        """
        Remove a registered product service.

        Args:
            product: The product type to remove.

        Returns:
            True if service was removed, False if it didn't exist.
        """
        return self.remove_service(product)
