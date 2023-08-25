import os
import random
import ftplib
from fastapi import FastAPI, Request
import json
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from conf import get_conf

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/clear")
def clear_queue():
    with open('queue.json') as f:
        data = json.load(f)
    with open('queue.json', 'w') as f:
        if len(data['queue']) > 0:
            data['queue'] = [data['queue'][0]]
        json.dump(data, f)
    return {"error": False}


@app.post("/remove/{song}")
def remove_from_queue(song: str):
    with open('queue.json') as f:
        data = json.load(f)
    data['queue'].remove(song)
    with open('queue.json', 'w') as f:
        json.dump(data, f)
    return {"error": False}


@app.get("/queue")
def get_queue():
    with open('queue.json') as f:
        data = json.load(f)
    return data['queue']


@app.get("/current")
def get_current():
    with open('queue.json') as f:
        data = json.load(f)
    return data['current']


def set_current(song):
    with open('queue.json') as f:
        data = json.load(f)
    data['current'] = song
    with open('queue.json', 'w') as f:
        json.dump(data, f)


def get_songs(conf):
    if conf['ftp']['enabled']:
        ftp = ftplib.FTP(conf['ftp']['host'])
        ftp.login(conf['ftp']['user'], conf['ftp']['pass'])
        ftp.cwd(conf["music_dir"])
        return ftp.nlst()
    try:
        return os.listdir(conf['music_dir'])
    except FileNotFoundError:
        raise FileNotFoundError("Music directory could not be found")


@app.get("/")
async def root(request: Request):
    conf = get_conf()
    return templates.TemplateResponse("index.html", {"request": request, "conf": conf, "queue": get_queue(),
                                                     "songs": get_songs(conf), "current": get_current(),
                                                     "remove_ext": os.path.splitext})


@app.post("/add/{song}")
async def add_to_queue(song: str):
    with open('queue.json') as f:
        data = json.load(f)
    data['queue'].append(song)
    with open('queue.json', 'w') as f:
        json.dump(data, f)
    return {"error": False}


@app.post("/current/{song}")
async def set_current_song(song: str):
    set_current(song)
    with open("queue.json") as f:
        data = json.load(f)
    with open('queue.json', 'w') as f:
        data['queue'].pop(0)
        json.dump(data, f)
    return {"error": False}


@app.get("/next")
async def next_up():
    queue = get_queue()
    if len(queue) > 0:
        song = queue.pop(0)
    else:
        song = random.choice(get_songs(get_conf()))
        with open("queue.json") as f:
            data = json.load(f)
        with open('queue.json', 'w') as f:
            data['queue'].insert(0, song)
            json.dump(data, f)
    return {"song": song}
