# HayBox CLI

Command line app for interacting with HayBox firmware

## Installation

### Windows EXE file

1. Download the exe file from the [latest release](https://github.com/JonnyHaystack/haybox-cli/releases)
2. Shift + right click in the directory you downloaded the exe to, then click "open command window here"
3. Run it with `.\haybox.exe`

### From PyPI

```
pip install -U --user haybox-cli
```

## Usage

```
Usage: haybox [OPTIONS] COMMAND [ARGS]...

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  config   Retrieve or update the active configuration on the device.
  devices  Scan for connected configurable HayBox devices.
  info     Print device info in JSON format for a specific HayBox device.
  reboot   Reboot the device to firmware or bootloader.
```
