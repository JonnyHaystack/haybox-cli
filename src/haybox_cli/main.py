from ast import List
import click
from haybox import haybox
import json


@click.group(context_settings=dict(help_option_names=["-h", "--help"], max_content_width=150))
@click.version_option()
def main():
    pass


@main.command("devices", help="Scan for connected configurable HayBox devices.")
def list_devices():
    devices: List[haybox.Controller] = haybox.scan_devices()
    for device in devices:
        print(f"Device on {device.serial_port.port}:")
        device_info = device.get_device_info()
        if device_info is None:
            return
        print(f"   Device name: {device_info['deviceName']}")
        print(f"   Firmware name: {device_info['firmwareName']}")
        print(f"   Firmware version: {device_info['firmwareVersion']}")


@main.command("info", help="Print device info in JSON format for a specific HayBox device.")
@click.option("--device", "-d", help="The serial port to connect to.")
def get_device_info(device):
    controller = haybox.Controller(device)
    device_info = controller.get_device_info()
    if device_info is None:
        return
    print(device_info)


@main.command("reboot", help="Reboot the device to firmware or bootloader.")
@click.option("--device", "-d", help="The serial port to connect to.")
@click.argument("reboot_to", type=click.Choice(["firmware", "bootloader"]), default="firmware")
def reboot(device, reboot_to):
    controller = haybox.Controller(device)
    if reboot_to == "firmware":
        controller.reboot_firmware()
    elif reboot_to == "bootloader":
        controller.reboot_bootloader()


@main.group("config", help="Retrieve or update the active configuration on the device.")
def config():
    pass


@config.command("get", help="Retrieve current configuration from device.")
@click.option("--device", "-d", help="The serial port to connect to.")
@click.option(
    "--output-to",
    "-o",
    type=click.Path(dir_okay=False, writable=True),
    help="A file to write the device's current configuration to.",
)
def get_config(device, output_to):
    controller = haybox.Controller(device)
    config_data = controller.get_config()
    if config_data is None:
        return

    if output_to is None:
        print(json.dumps(controller.get_config(), indent=2))
        return

    with open(output_to, "w") as f:
        json.dump(controller.get_config(), f, indent=2)


@config.command("set", help="Update the configuration on the device.")
@click.option("--device", "-d", help="The serial port to connect to.")
@click.argument("file")
def set_config(device, file):
    controller = haybox.Controller(device)
    with open(file) as f:
        config_dict = json.load(f)
    controller.set_config(config_dict)


if __name__ == "__main__":
    main()
