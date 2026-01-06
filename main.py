import ctypes
import os
import time
from enum import StrEnum, IntEnum

class DeviceApi(StrEnum):
    WASAPI = 'wdm'
    KERNEL_STREAMING = 'ks'
    MULTIMEDIA = 'mme'
    ASIO = 'asio'

class InputChannel(IntEnum):
    INPUT_1 = 0
    INPUT_2 = 1
    INPUT_3 = 2
    INPUT_4 = 3

# START USER CONFIG #
VOICEMEETER_PATH = "C:/Program Files (x86)/VB/Voicemeeter/"

INPUT_CHANNEL = InputChannel.INPUT_1

PREFERRED_INPUT = "M-Track Solo"
PREFERRED_INPUT_API = DeviceApi.KERNEL_STREAMING

FALLBACK_INPUT = "Integrated Microphone"
FALLBACK_INPUT_API = DeviceApi.WASAPI

POLL_INTERVAL_S = 5.0
PRINT_DEBUG = False
# END USER CONFIG #

DEV_TYPE_TO_API = {
    1: DeviceApi.MULTIMEDIA,
    3: DeviceApi.WASAPI,
    4: DeviceApi.KERNEL_STREAMING,
    5: DeviceApi.ASIO,
}

def load_vmr(dll_path: str):
    vmr = ctypes.WinDLL(dll_path)

    vmr.VBVMR_Login.restype = ctypes.c_long
    vmr.VBVMR_Logout.restype = ctypes.c_long

    vmr.VBVMR_SetParameterFloat.argtypes = [ctypes.c_char_p, ctypes.c_float]
    vmr.VBVMR_SetParameterFloat.restype = ctypes.c_long

    vmr.VBVMR_SetParameterStringA.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    vmr.VBVMR_SetParameterStringA.restype = ctypes.c_long

    vmr.VBVMR_Input_GetDeviceNumber.restype = ctypes.c_long
    vmr.VBVMR_Input_GetDeviceDescA.argtypes = [
        ctypes.c_long,
        ctypes.POINTER(ctypes.c_long),
        ctypes.c_char_p,
        ctypes.c_char_p,
    ]
    vmr.VBVMR_Input_GetDeviceDescA.restype = ctypes.c_long

    return vmr


def all_devices(vmr):
    MAX_NAME_SIZE = 512
    nb = int(vmr.VBVMR_Input_GetDeviceNumber())

    devices = {}

    for i in range(nb):
        dev_type = ctypes.c_long(0)
        name_buf = ctypes.create_string_buffer(MAX_NAME_SIZE)
        hwid_buf = ctypes.create_string_buffer(MAX_NAME_SIZE)

        if vmr.VBVMR_Input_GetDeviceDescA(i, ctypes.byref(dev_type), name_buf, hwid_buf) != 0:
            continue

        api = DEV_TYPE_TO_API.get(int(dev_type.value))
        if api is None:
            continue

        name = name_buf.value.decode("mbcs", errors="replace")
        hwid = hwid_buf.value.decode("mbcs", errors="replace")
        if not hwid or not name:
            continue

        devices.setdefault(hwid, {}).setdefault(api, [])
        if name not in devices[hwid][api]:
            devices[hwid][api].append(name)

    for hwid in devices:
        for api in devices[hwid]:
            devices[hwid][api].sort()

    return devices


def preferred_device(devices):
    def sanitize(x: str):
        return (x or "").lower().strip().replace('(', '').replace(')', '')

    def find_match(wanted_name: str, wanted_api: DeviceApi):
        x = sanitize(wanted_name)
        if not x:
            return None

        # Exact match
        for hwid, by_api in devices.items():
            for name in by_api.get(wanted_api, []):
                if sanitize(name) == x:
                    return hwid, name

        # Loose match
        for hwid, by_api in devices.items():
            for name in by_api.get(wanted_api, []):
                if x in sanitize(name):
                    return hwid, name

        return None

    for name, api in (
        (PREFERRED_INPUT, PREFERRED_INPUT_API),
        (FALLBACK_INPUT, FALLBACK_INPUT_API),
    ):
        hit = find_match(name, api)
        if hit:
            hwid, public_name = hit
            return hwid, public_name, api

    return None, None, None


def set_device(vmr, device_name, device_api):
    param = f"Strip[{INPUT_CHANNEL}].device.{device_api}".encode("ascii")
    return vmr.VBVMR_SetParameterStringA(param, device_name.encode("mbcs", errors="replace"))


def restart_audio_engine(vmr):
    print("Restart Audio Engine")
    return vmr.VBVMR_SetParameterFloat(b"Command.Restart", ctypes.c_float(1.0))


def monitor_forever(dll_path):
    vmr = load_vmr(dll_path)

    ret = vmr.VBVMR_Login()
    if ret < 0:
        raise SystemExit(f"vbvmr_login failed: {ret}")

    try:
        current_hwid = None
        while True:
            time.sleep(POLL_INTERVAL_S)
            devices = all_devices(vmr)
            preferred_hwid, preferred_name, preferred_api = preferred_device(devices)

            if PRINT_DEBUG:
                print("\n=== Devices ===")
                for hwid, by_api in devices.items():
                    print("")
                    tag = "[PREFERRED] " if hwid == preferred_hwid else ""
                    print(f"{tag}{hwid}")
                    for api, names in by_api.items():
                        for n in names:
                            print(f"   - {api}: {n}")
                print("")

            if preferred_hwid != current_hwid:
                if preferred_hwid:
                    ret = set_device(vmr, preferred_name, preferred_api)
                    if ret < 0:
                        print(f'set_device Failed ({ret})')
                        break
                    print(f'Set "Input {INPUT_CHANNEL + 1}" to "{preferred_api}: {preferred_name}"')
                ret = restart_audio_engine(vmr)
                if ret < 0:
                    print(f'restart_audio_engine Failed ({ret})')
                    break
                current_hwid = preferred_hwid

    finally:
        vmr.VBVMR_Logout()

def main():
    dll_path = os.path.join(VOICEMEETER_PATH, "VoicemeeterRemote64.dll")
    if not os.path.exists(dll_path):
        raise SystemExit(f"Voicemeter not found: {dll_path}")

    while True:
        try:
            monitor_forever(dll_path)
        except Exception as e:
            print(e)
        time.sleep(POLL_INTERVAL_S)

if __name__ == "__main__":
    main()
