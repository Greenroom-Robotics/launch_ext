"""Module for the MakeDeviceNode action."""

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
    """Glob a path using a regular expression."""
    results = []
    for p in path.glob("*"):
        if pattern.match(p.name) is None:
            continue

        if directory is not None:
            if p.is_dir() != directory:
                continue
        
        results.append(p)
    return results

class MakeDeviceNode(Action):
    """Action that logs a message when executed."""

    def __init__(self, target_node: SomeSubstitutionsType, device_type: SomeSubstitutionsType,
                 manufacturer: SomeSubstitutionsType, product: SomeSubstitutionsType, use_id: bool=False, **kwargs):
        """Create a MakeDeviceNode action."""
        super().__init__(**kwargs)

        self.__target_node = normalize_to_list_of_substitutions(target_node)
        self.__device_type = normalize_to_list_of_substitutions(device_type)
        self.__manufacturer = normalize_to_list_of_substitutions(manufacturer)
        self.__product = normalize_to_list_of_substitutions(product)
        self.__use_id = use_id

    def find_usb_port(self, manufacturer: Optional[str]=None, product: Optional[str]=None) -> Optional[Path]:
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
        for usb_config in re_glob_path(usb_dev, USB_CONFIG_RE, directory=True):
            if device_type == "ttyUSB":
                # find the device node?
                for usb_interface in usb_config.glob("ttyUSB*/tty/ttyUSB*"):
                    return usb_interface
                
        return None


    def execute(self, context: LaunchContext) -> None:
        """Execute the action."""

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

        subprocess.run(["sudo", "mknod", target_node, "c", major, minor]).check_returncode()
        subprocess.run(["sudo", "chgrp", "dialout", target_node]).check_returncode()
        subprocess.run(["sudo", "chmod", "0660", target_node]).check_returncode()

        return None
