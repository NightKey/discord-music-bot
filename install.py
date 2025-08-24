import service
from os import getcwdb
import subprocess

try:
    with open("dmb.service.template", 'r') as f:
        service = f.read(-1)
    service = service.replace(
        "<folder_path>", f'{getcwdb().decode("utf-8")}').replace("<file_name>", "service.py")
    with open("/etc/systemd/system/dmb.service", "w") as f:
        f.write(service)
    subprocess.call(["sudo", "systemctl", "daemon-reload"])
    subprocess.call(["sudo", "systemctl", "enable",
                    "dmb.service"])
    subprocess.call(["sudo", "systemctl", "start",
                    "dmb.service"])
except Exception as ex:
    print("Service creation failed, please try starting this with sudo!")
