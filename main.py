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


def read_packet():
    raw_data = []

    # bytes_read = serial_port.read_until(b'\x00')
    while True:
        bytes_read = serial_port.read(1)
        if len(bytes_read) < 1:
            return None
        byte = bytes_read[0]
        if byte == 0:
            break
        raw_data.append(byte)

    try:
        decoded_data = cobs.decode(bytearray(raw_data))
    except cobs.DecodeError as e:
        print(e)
        return None

    if len(decoded_data) <= 0:
        return None

    return decoded_data


def write_packet(command_id: int, arg: bytes = None):
    raw_data = bytes([command_id])
    if arg is not None:
        raw_data += arg

    try:
        encoded_data = cobs.encode(raw_data)
        encoded_data += bytes([0])
        written_len = serial_port.write(encoded_data)
        if written_len < len(encoded_data):
            return False
    except TypeError as e:
        print(e)
        return False

    return True


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
    # print("Sending CMD_GET_DEVICE_INFO...")
    # write_packet(config_pb2.CMD_GET_DEVICE_INFO)
    # print("Finished sending")
    # print("Waiting for response...")
    # response = read_packet()
    # print(f"Received response {response}")
    # if response is None or len(response) <= 0:
    #     return
    # if response[0] == config_pb2.CMD_SET_DEVICE_INFO:
    #     device_info = config_pb2.DeviceInfo()
    #     device_info.ParseFromString(response[1:])
    #     # print(device_info)
    #     print(json.dumps(MessageToDict(device_info), indent=2))
    # elif response[0] == config_pb2.CMD_ERROR:
    #     print(f"Error: {str(response[1:])}\n")


@main.command("get-config")
@click.option("--device", "-d")
def get_config(device):
    controller = haybox.Controller(device)
    # with open("config.json", "w") as f:
    # json.dump(controller.get_config(), f, indent=2)
    print(json.dumps(controller.get_config(), indent=2))


@main.command("set-config")
@click.option("--device", "-d")
def set_config(device):
    controller = haybox.Controller(device)
    print("Opening and parsing config file to dict...")
    with open("config.json") as f:
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


"""
try:
    # Find serial port
    device_info: ListPortInfo = None

    for comport in list_ports.comports():
        if comport.vid == 0x2E8A and comport.pid == 0x000A:
            device_info = comport

    if device_info is None:
        print("No devices found")
        exit(0)

    print(device_info.name)
    serial_port = Serial(port=device_info.name, baudrate=115200)

    # Execute commands
    get_device_info()
    get_config()
    # set_config()
    # time.sleep(0.5)
    # reboot_firmware()
    # reboot_bootloader()
except SerialException as e:
    print(f"Error occurred when opening serial port: {e}")
except KeyboardInterrupt:
    print("Serial communication stopped.")
finally:
    if serial_port is not None:
        serial_port.close()
"""


if __name__ == "__main__":
    main()
