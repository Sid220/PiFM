import shutil
import subprocess
import threading
import time

import conf

subprocess.run(["bash", "-c", "sudo echo '[+] sudo enabled'"])
config = conf.get_conf()


def run_ui():
    shutil.copy("assets/queue.json", "queue.json")
    subprocess.run(
        ["bash", "-c", "python3 -m uvicorn main:app --host 0.0.0.0 --port " + str(config["ui"]["port"])])


if config["ui"]["enabled"]:
    ui_thread = threading.Thread(target=run_ui)
    ui_thread.start()
    time.sleep(5)

subprocess.run(["python3", "radio.py"])
