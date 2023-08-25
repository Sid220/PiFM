import json
import subprocess
from conf import get_conf


def detect_model() -> str:
    with open('/proc/device-tree/model') as f:
        model = f.read()
    return model


try:
    model = detect_model()
except FileNotFoundError:
    print("This script must be run on a Raspberry Pi")
    exit(1)

rpi4 = "Raspberry Pi 4" in model

subprocess.run(
    ["bash", "-c", "sudo apt update && sudo apt-get install -y ffmpeg make build-essential libraspberrypi-dev"])
subprocess.run(["bash", "-c", "git clone https://github.com/markondej/fm_transmitter"])
subprocess.run(["bash", "-c", "pip install -r requirements.txt"])
if rpi4:
    subprocess.run(["bash", "-c", "cd fm_transmitter && make GPIO21=1"])
    subprocess.run(["bash", "-c", 'echo "powersave"| sudo tee /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor'])
else:
    subprocess.run(["bash", "-c", "cd fm_transmitter && make"])

conf = get_conf()

print("Welcome to PiFM!")


def q_freq():
    print("What frequency would you like to broadcast on? [88.6]", end=" ")
    freq = input()
    if freq == "":
        freq = "88.6"

    try:
        freq = float(freq)
    except ValueError:
        print("Please enter a valid frequency")
        q_freq()

    if freq > 108 or freq < 87.5:
        print("Please enter a frequency between 87.5 and 108")
        q_freq()
    elif freq > 93 and rpi4:
        print("High frequencies are known to be problomatic on Raspberry Pi 4")
        print("Continue anyway? [y/N]:", end=" ")
        if input().lower() not in ["yes", "y"]:
            q_freq()

    if len(str(freq).split(".")[1]) > 1:
        print("Please enter a frequency with a step of 0.1")
        q_freq()

    conf["freq"] = freq


q_freq()

print("Would you like to use FTP to retrieve your music? [y/N]:", end=" ")
ftp = False
if input().lower() in ["yes", "y"]:
    ftp = True
    print("Please enter your FTP username", end=" ")
    username = input()
    print("Please enter your FTP password", end=" ")
    password = input()
    print("Please enter your FTP host", end=" ")
    host = input()
    print("Please enter your FTP port", end=" ")
    port = input()
    print("Please enter your FTP directory", end=" ")

    conf["ftp"] = {
        "enabled": True,
        "port": port,
        "host": host,
        "user": username,
        "pass": password,
    }

print("Music directory" if not ftp else "Music directory (relative to FTP root)",
      end=": ")
music_dir = input()
conf["music_dir"] = music_dir

print("Would you like to have an automated news service on your radio [Y/n]:", end=" ")
conf["news"]["enabled"] = input().lower() in ["yes", "y", ""]

print("Would you like to have a web interface for your radio [Y/n]:", end=" ")
conf["ui"]["enabled"] = input().lower() in ["yes", "y", ""]

print("Writing config file...")
if input().lower() in ["yes", "y", ""]:
    with open('conf.json', 'w') as f:
        json.dump(conf, f)
print("Done.")
