"""Actions for creating Linux device nodes for USB devices.

This module provides functionality to create device nodes for USB devices
that are not automatically created by the kernel or when udev is not available.
"""

from typing import List, Optional
from pathlib import Path
import re
import subprocess

import launch.logging

from launch.action import Action
from launch.launch_context import LaunchContext
from launch.some_substitutions_type import SomeSubstitutionsType
from launch.utilities import normalize_to_list_of_substitutions, perform_substitutions

USB_PORT_RE = re.compile(r"(\d+)\-(\d+)(\.\d+)*")
USB_CONFIG_RE = re.compile(r"(\d+)\-(\d+)(\.\d+)*:(\d+)\.(\d+)")

def re_glob_path(path: Path, pattern: re.Pattern, directory: Optional[bool]=None) -> List[Path]:
    """Glob a path using a regular expression pattern.

    Args:
        path: Directory path to search in
        pattern: Compiled regular expression pattern to match against
        directory: If True, only match directories; if False, only match files; if None, match both

    Returns:
        List of Path objects matching the pattern
    """
    results = []
    for p in path.glob("*"):
        if pattern.match(p.name) is None:
            continue

        if directory is not None:
            if p.is_dir() != directory:
                continue
        
        results.append(p)
    return results


def create_device_node(target_node: str, major: str, minor: str) -> None:
    """Create a character device node with appropriate permissions.

    Args:
        target_node: Path where the device node should be created
        major: Major device number
        minor: Minor device number

    Raises:
        subprocess.CalledProcessError: If any of the device creation commands fail
    """
    subprocess.run(["sudo", "mknod", target_node, "c", major, minor]).check_returncode()
    subprocess.run(["sudo", "chgrp", "dialout", target_node]).check_returncode()
    subprocess.run(["sudo", "chmod", "0660", target_node]).check_returncode()


class MakeDeviceNodeFromPath(Action):
    """Create a device node from a specific device path in sysfs.

    This action creates a device node at the specified target path using
    device information from a sysfs device path.
    """

    def __init__(self, target_node: SomeSubstitutionsType, device_path: SomeSubstitutionsType, **kwargs):
        """Initialize the MakeDeviceNodeFromPath action.

        Args:
            target_node: Path where the device node should be created
            device_path: Path to the device in sysfs (e.g., /sys/class/tty/ttyUSB0)
            **kwargs: Additional arguments passed to the parent Action class
        """
        super().__init__(**kwargs)

        self.__target_node = normalize_to_list_of_substitutions(target_node)
        self.__device_path = normalize_to_list_of_substitutions(device_path)

    def execute(self, context: LaunchContext) -> None:
        """Execute the action."""

        target_node = perform_substitutions(context, self.__target_node)
        device_path = perform_substitutions(context, self.__device_path)

        if Path(target_node).exists():
            launch.logging.get_logger('launch.user').info(f"Device node {target_node} already exists")
            return None

        device_sysfs_path = Path(device_path)
        if not device_sysfs_path.exists():
            launch.logging.get_logger('launch.user').error(f"Could not find device path '{device_path}'")
            return None

        launch.logging.get_logger('launch.user').info(f"Creating device node {target_node} from {device_path}")

        major, minor = (device_sysfs_path / "dev").read_text().strip().split(":")
        create_device_node(target_node, major, minor)

        return None


class MakeUSBDeviceNodesFromPortPath(Action):
    """Create USB device nodes from a port path.

    This action creates device nodes for USB devices found at a specific
    USB port path in the sysfs filesystem.
    """

    def __init__(self, port_path: SomeSubstitutionsType, **kwargs):
        """Initialize the MakeUSBDeviceNodesFromPortPath action.

        Args:
            port_path: Path to the USB port in sysfs
            **kwargs: Additional arguments passed to the parent Action class
        """
        super().__init__(**kwargs)

        self.__port_path = normalize_to_list_of_substitutions(port_path)

    def execute(self, context: LaunchContext) -> None:
        """Execute the action to create device nodes from USB port path.

        Args:
            context: The launch context containing substitution values

        Returns:
            None
        """
        port_path = perform_substitutions(context, self.__port_path)

        device_sysfs_path = Path(port_path)
        if not device_sysfs_path.exists():
            launch.logging.get_logger('launch.user').error(f"Could not find device path '{port_path}'")
            return None

        launch.logging.get_logger('launch.user').info(f"Processing USB devices from port path {port_path}")

        # This class appears to be incomplete - it doesn't define target_node
        # This should be fixed by adding a target_node parameter to __init__
        launch.logging.get_logger('launch.user').warn("MakeUSBDeviceNodesFromPortPath is incomplete - missing target_node parameter")

        return None

class MakeDeviceNode(Action):
    """Create device nodes for USB devices by manufacturer and product.

    This action searches for USB devices by their manufacturer and product
    names, then creates a device node at the specified target path.
    """

    def __init__(self, target_node: SomeSubstitutionsType, device_type: SomeSubstitutionsType,
                 manufacturer: SomeSubstitutionsType, product: SomeSubstitutionsType, use_id: bool=False, **kwargs):
        """Initialize the MakeDeviceNode action.

        Args:
            target_node: Path where the device node should be created
            device_type: Type of device (e.g., 'ttyUSB')
            manufacturer: USB device manufacturer name or ID
            product: USB device product name or ID
            use_id: If True, use vendor/product IDs instead of names
            **kwargs: Additional arguments passed to the parent Action class
        """
        super().__init__(**kwargs)

        self.__target_node = normalize_to_list_of_substitutions(target_node)
        self.__device_type = normalize_to_list_of_substitutions(device_type)
        self.__manufacturer = normalize_to_list_of_substitutions(manufacturer)
        self.__product = normalize_to_list_of_substitutions(product)
        self.__use_id = use_id

    def find_usb_port(self, manufacturer: Optional[str]=None, product: Optional[str]=None) -> Optional[Path]:
        """Find USB port path by manufacturer and product.

        Args:
            manufacturer: Manufacturer name or vendor ID to search for
            product: Product name or product ID to search for

        Returns:
            Path to the USB device if found, None otherwise
        """
        for usb_dev in re_glob_path(Path("/sys/bus/usb/devices"), USB_PORT_RE, directory=True):
            if not self.__use_id:
                manufacturer_f = (usb_dev / "manufacturer")
                product_f = (usb_dev / "product")
            else:
                manufacturer_f = (usb_dev / "idVendor")
                product_f = (usb_dev / "idProduct")

            if not manufacturer_f.exists():
                continue
            if not product_f.exists():
                continue

            if manufacturer != manufacturer_f.read_text().strip():
                continue
            if product != product_f.read_text().strip():
                continue
            return usb_dev

        return None

    def find_usb_interface(self, usb_dev: Path, device_type: str) -> Optional[Path]:
        """Find USB interface for the specified device type.

        Args:
            usb_dev: Path to the USB device in sysfs
            device_type: Type of interface to find (e.g., 'ttyUSB')

        Returns:
            Path to the USB interface if found, None otherwise
        """
        for usb_config in re_glob_path(usb_dev, USB_CONFIG_RE, directory=True):
            if device_type == "ttyUSB":
                # find the device node?
                for usb_interface in usb_config.glob("ttyUSB*/tty/ttyUSB*"):
                    return usb_interface

        return None

    def execute(self, context: LaunchContext) -> None:
        """Execute the action to create the device node.

        Searches for the USB device by manufacturer and product, then creates
        a device node at the target path if the device is found.

        Args:
            context: The launch context containing substitution values

        Returns:
            None
        """
        target_node = perform_substitutions(context, self.__target_node)
        device_type = perform_substitutions(context, self.__device_type)
        manufacturer = perform_substitutions(context, self.__manufacturer)
        product = perform_substitutions(context, self.__product)

        if Path(target_node).exists():
            launch.logging.get_logger('launch.user').info(f"Device node {target_node} already exists")
            return None

        usb_dev = self.find_usb_port(manufacturer, product)
        if usb_dev is None:
            launch.logging.get_logger('launch.user').error(f"Could not find USB device {manufacturer} {product}")
            return None
        
        usb_interface = self.find_usb_interface(usb_dev, device_type)
        if usb_interface is None:
            launch.logging.get_logger('launch.user').error(f"Could not find USB interface {device_type} for {manufacturer} {product}")
            return None

        launch.logging.get_logger('launch.user').info(f"Creating device node {target_node} for {manufacturer} {product}")

        major, minor = (usb_interface / "dev").read_text().strip().split(":")

        create_device_node(target_node, major, minor)

        return None
