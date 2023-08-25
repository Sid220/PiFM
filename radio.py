import datetime
import os
import shutil
import subprocess
import threading
from tempfile import NamedTemporaryFile
import ffmpeg
import conf
import random
import requests
import time
import ftplib
import conf

config = conf.get_conf()

# Create thread to run the radio
def run_radio():
    print("Running radio")
    subprocess.run(["bash", "-c", "sudo modprobe snd-aloop"])
    subprocess.run(["bash", "-c", """
CARD=$(cat /proc/asound/cards | grep "Loopback" | awk '{print $1}' | head -1)
if [ -z "$CARD" ]; then
    echo "Loopback device not found"
    exit 1
fi
echo "defaults.pcm.card $CARD
defaults.ctl.card $CARD" | sudo tee /etc/asound.conf
arecord -D hw:3,1,0 -c 2 -d 0 -r 22050 -f S16_LE | sudo ./fm_transmitter/fm_transmitter -f """
                    + str(config["freq"]) + " -"])


def play_song(song):
    print("Playing song " + song)
    subprocess.run(["aplay", song])


def exit_err():
    print("Error")
    exit(1)


radio = threading.Thread(target=run_radio)
radio.start()
time.sleep(5)

song_thread = threading.Thread(target=play_song,
                               args=("./fm_transmitter/acoustic_guitar_duet.wav",))
song_thread.start()

last_report = datetime.datetime.now() - datetime.timedelta(hours=2, minutes=1)

while True:
    print("Getting next song")
    # Get next song
    if config["ui"]["enabled"]:
        song = requests.get("http://localhost:" + str(config["ui"]["port"]) + "/next").json()["song"]
    else:
        if config["ftp"]["enabled"]:
            ftp = ftplib.FTP(config['ftp']['host'])
            ftp.login(config['ftp']['user'], config['ftp']['pass'])
            ftp.cwd(config["music_dir"])
            songs = ftp.nlst()
            song = random.choice(songs)
        else:
            song = random.choice(os.listdir(config["music_dir"]))
    print("Next song is " + song)

    song_file = NamedTemporaryFile(suffix='.mp3')
    export_file = NamedTemporaryFile(suffix='.wav')

    if config["ftp"]["enabled"]:
        ftp = ftplib.FTP(config['ftp']['host'])
        ftp.login(config['ftp']['user'], config['ftp']['pass'])
        ftp.cwd(config["music_dir"])

        try:
            with open(song_file.name, "wb+") as tmp:
                ftp.retrbinary("RETR " + song, tmp.write)
        except Exception as e:
            print(e)
            exit_err()
    else:
        try:
            shutil.copy(os.path.join(config["music_dir"], song), song_file.name)
        except Exception as e:
            print(e)
            exit_err()

    # Convert next song
    print("Converting next song")

    in_one = ffmpeg.input(song_file.name)
    if config["slogan"]["enabled"]:
        in_two = ffmpeg.input(
            random.choice(config["slogan"]["files"]))
        stream = ffmpeg.concat(in_one, in_two, v=0, a=1)
    else:
        stream = in_one
    stream = ffmpeg.output(stream, export_file.name, acodec='pcm_s16le', ac=2, ar=22050)
    ffmpeg.run(stream, overwrite_output=True)

    show_report = (6 <= datetime.datetime.now().hour < 20) and (
            last_report < (datetime.datetime.now() - datetime.timedelta(hours=2))) and config["news"]["enabled"]
    if show_report:
        print("News Report")
        subprocess.run(["python3", "news.py"])

    print("Waiting on previous song")
    song_thread.join()

    if show_report:
        play_song("out.wav")
        last_report = datetime.datetime.now()

    song_thread = threading.Thread(target=play_song, args=(export_file.name,))
    song_thread.start()
    if config["ui"]["enabled"]:
        requests.post("http://localhost:" + str(config["ui"]["port"]) + "/current/" + song)
    time.sleep(1)
