import click
from haybox import haybox
import json
import time

from cobs import cobs
from google.protobuf.json_format import MessageToDict, Parse, ParseDict
from serial import Serial
from serial import SerialException
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

from proto import config_pb2


@click.group(context_settings=dict(help_option_names=["-h", "--help"], max_content_width=150))
@click.version_option()
def main():
    pass


@main.command("list-devices")
def list_devices():
    devices: [haybox.Controller] = haybox.scan_devices()
    for device in devices:
        print(f"{device.serial_port.port}")


@main.command("device-info")
@click.option("--device", "-d")
def get_device_info(device):
    controller = haybox.Controller(device)
    print(controller.get_device_info())


@main.command("get-config")
@click.option("--device", "-d")
@click.option("--output-to", "-o")
def get_config(device, output_to):
    controller = haybox.Controller(device)
    if output_to is None:
        print(json.dumps(controller.get_config(), indent=2))
        return

    with open(output_to, "w") as f:
        json.dump(controller.get_config(), f, indent=2)


@main.command("set-config")
@click.option("--device", "-d")
@click.argument("file")
def set_config(device, file):
    controller = haybox.Controller(device)
    print("Opening and parsing config file to dict...")
    with open(file) as f:
        config_dict = json.load(f)
    controller.set_config(config_dict)


@main.command("reboot")
@click.option("--device", "-d")
@click.argument(
    "reboot_to",
    type=click.Choice(["firmware", "bootloader"]),
    default="firmware",
)
def reboot(device, reboot_to):
    controller = haybox.Controller(device)
    if reboot_to == "firmware":
        controller.reboot_firmware()
    elif reboot_to == "bootloader":
        controller.reboot_bootloader()


def reboot_firmware():
    print("Sending CMD_REBOOT_FIRMWARE...")
    write_packet(config_pb2.CMD_REBOOT_FIRMWARE)
    print("Finished sending")


def reboot_bootloader():
    print("Sending CMD_REBOOT_BOOTLOADER...")
    write_packet(config_pb2.CMD_REBOOT_BOOTLOADER)
    print("Finished sending")


if __name__ == "__main__":
    main()
