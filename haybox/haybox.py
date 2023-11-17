from cobs import cobs
from google.protobuf.json_format import MessageToDict, ParseDict
from serial import Serial
from serial import SerialException
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

from proto import config_pb2


class Controller:
    def __init__(self, port_name: str):
        self.serial_port = Serial()
        self.serial_port.port = port_name
        self.serial_port.baudrate = 115200
        self.serial_port.timeout = 0.1

    def read_packet(self):
        if not self.serial_port.is_open:
            return False

        raw_data = []

        # bytes_read = serial_port.read_until(b'\x00')
        while True:
            bytes_read = self.serial_port.read(1)
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

    def write_packet(self, command_id: int, arg: bytes = None):
        if not self.serial_port.is_open:
            return False

        raw_data = bytes([command_id])
        if arg is not None:
            raw_data += arg

        try:
            encoded_data = cobs.encode(raw_data)
            encoded_data += bytes([0])
            written_len = self.serial_port.write(encoded_data)
            if written_len < len(encoded_data):
                return False
        except TypeError as e:
            print(e)
            return False

        return True

    def get_device_info(self):
        try:
            self.serial_port.open()
            # print("Sending CMD_GET_DEVICE_INFO...")
            self.write_packet(config_pb2.CMD_GET_DEVICE_INFO)
            # print("Finished sending")
            # print("Waiting for response...")
            response = self.read_packet()
            # print(f"Received response {response}")
            if response is None or len(response) <= 0:
                return None
            if response[0] == config_pb2.CMD_SET_DEVICE_INFO:
                device_info = config_pb2.DeviceInfo()
                device_info.ParseFromString(response[1:])
                return MessageToDict(device_info)
            elif response[0] == config_pb2.CMD_ERROR:
                print(f"Error: {str(response[1:])}\n")
        except SerialException as e:
            print(f"Error occurred when opening serial port: {e}")
        finally:
            self.serial_port.close()

    def get_config(self):
        try:
            self.serial_port.open()
            print("Sending CMD_GET_CONFIG...")
            self.write_packet(config_pb2.CMD_GET_CONFIG)
            print("Finished sending")
            print("Waiting for response...")
            response = self.read_packet()
            # print(f"Received response {response}")
            if response is None or len(response) <= 0:
                return
            if response[0] == config_pb2.CMD_SET_CONFIG:
                config = config_pb2.Config()
                config.ParseFromString(response[1:])
                return MessageToDict(config)
            elif response[0] == config_pb2.CMD_ERROR:
                print(f"Error: {str(response[1:])}\n")
        except SerialException as e:
            print(f"Error occurred when opening serial port: {e}")
        finally:
            self.serial_port.close()

    def set_config(self, config_dict: dict):
        try:
            self.serial_port.open()
            print("Opening and parsing config file...")
            config = config_pb2.Config()
            ParseDict(config_dict, config)
            print("Serializing to wire format...")
            config_encoded = config.SerializeToString()

            # print(json.dumps(MessageToDict(config), indent=2))
            # print(config_encoded)
            # print(len(config_encoded))

            print("Sending CMD_SET_CONFIG...")
            self.write_packet(config_pb2.CMD_SET_CONFIG, config_encoded)
            print("Finished sending")
            print("Waiting for response...")
            response = self.read_packet()
            if response[0] == config_pb2.CMD_ERROR:
                print(f"Error: {str(response[1:])}\n")
            elif response[0] == config_pb2.CMD_SUCCESS:
                print("Success!")
        except SerialException as e:
            print(f"Error occurred when opening serial port: {e}")
        finally:
            self.serial_port.close()

    def reboot_firmware(self):
        try:
            self.serial_port.open()
            print("Sending CMD_REBOOT_FIRMWARE...")
            self.write_packet(config_pb2.CMD_REBOOT_FIRMWARE)
            print("Finished sending")
        except SerialException as e:
            print(f"Error occurred when opening serial port: {e}")
        finally:
            self.serial_port.close()

    def reboot_bootloader(self):
        try:
            self.serial_port.open()
            print("Sending CMD_REBOOT_BOOTLOADER...")
            self.write_packet(config_pb2.CMD_REBOOT_BOOTLOADER)
            print("Finished sending")
        except SerialException as e:
            print(f"Error occurred when opening serial port: {e}")
        finally:
            self.serial_port.close()


def scan_devices():
    for comport in list_ports.comports():
        if comport.vid == 0x2E8A and comport.pid == 0x000A:
            yield Controller(comport.name)
