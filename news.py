import subprocess
from datetime import datetime

import ffmpeg
from pytube import YouTube
import requests
from tempfile import NamedTemporaryFile
import xml.etree.ElementTree as ET
from gtts import gTTS
import conf

config = conf.get_conf()

audio_file = None

if config["news"]["youtube"]["enabled"]:
    latest = (
        requests.get("https://yt.lemnoslife.com/noKey/search?part=id&channelId=" + config["news"]["youtube"][
            "channel"] + "&order=date")
        .json())

    for item in latest["items"]:
        if item["id"]["kind"] != "youtube#video":
            continue

        video = item["id"]["videoId"]

        temp = NamedTemporaryFile()
        yt = YouTube("https://www.youtube.com/watch?v=" + video)
        vid = yt.streams.filter(only_audio=True).first()
        print(vid.default_filename)
        if config["news"]["bbc"]:
            if not vid.default_filename.endswith("- BBC News.mp4"):
                continue

        audio_file = vid.download(filename=temp.name + ".mp3")
        print("Downloaded " + audio_file)

        # Check video length
        if float(ffmpeg.probe(audio_file)['format']['duration']) < (60 * 10):
            print("Found appropriate video")
            break

    print(audio_file)

if config["news"]["rss"]["enabled"]:
    news = requests.get(config["news"]["rss"]["url"]).text

    # Parse RSS file and extract each "description" field
    # create element tree object
    tree = ET.ElementTree(ET.fromstring(news))

    # get root element
    root = tree.getroot()

    newsitems = []

    for item in root.findall('./channel/item'):
        newsitems.append({
            "title": item.find("title").text,
            "desc": item.find("description").text
        })

    newsitems = newsitems[:config["news"]["rss"]["max_headlines"]]
    now = datetime.now()

    current_time = now.strftime("%H:%M")

    text = "Welcome to the news, it is currently " + current_time + ". Here are the top stories from around the world: "
    for item in newsitems:
        text += item["title"] + " - " + item["desc"] + " "
    if config["news"]["youtube"]["enabled"] and config["news"]["bbc"]:
        text += "Now let's delve deeper with the BBC."
    elif config["news"]["youtube"]["enabled"]:
        text += "Now let's delve deeper."
    print(text)
    tts = gTTS(
        text=text,
        lang='en',
        tld='co.uk')
    tts.save('news.mp3')

if config["news"]["youtube"]["enabled"] and config["news"]["rss"]["enabled"] and config["news"]["intro"]["enabled"]:
    auto_anchor = ffmpeg.input('news.mp3')
    news_file = ffmpeg.input(audio_file)
    intro_file = ffmpeg.input(config["news"]["intro"]["file"])
    (ffmpeg
     .concat(intro_file.audio.filter('atrim', duration=43),
             ffmpeg.filter(
                 [intro_file.audio.filter('atrim', start=43),
                  ffmpeg.concat(
                      auto_anchor,
                      news_file, v=0, a=1
                  )
                  ],
                 "amix"
             ),
             v=0, a=1)
     .filter('atrim', duration=(int(float(ffmpeg.probe(audio_file)['format']['duration'])) +
                                int(float(ffmpeg.probe('news.mp3')['format']['duration'])) +
                                (2 * 45)))
     .output("out.wav", acodec='pcm_s16le', ac=2, ar=22050)
     .run(overwrite_output=True))

elif config["news"]["youtube"]["enabled"] and (not config["news"]["rss"]["enabled"]) and config["news"]["intro"][
    "enabled"]:
    news_file = ffmpeg.input(audio_file)
    intro_file = ffmpeg.input(config["news"]["intro"]["file"])
    (ffmpeg
     .concat(intro_file.audio.filter('atrim', duration=43),
             ffmpeg.filter(
                 [intro_file.audio.filter('atrim', start=43),
                  news_file
                  ],
                 "amix"
             ),
             v=0, a=1)
     .filter('atrim', duration=(int(float(ffmpeg.probe(audio_file)['format']['duration'])) +
                                (2 * 45)))
     .output("out.wav", acodec='pcm_s16le', ac=2, ar=22050)
     .run(overwrite_output=True))

elif config["news"]["rss"]["enabled"] and not config["news"]["youtube"]["enabled"] and config["news"]["intro"][
    "enabled"]:
    auto_anchor = ffmpeg.input('news.mp3')
    intro_file = ffmpeg.input(config["news"]["intro"]["file"])
    (ffmpeg
     .concat(intro_file.audio.filter('atrim', duration=43),
             ffmpeg.filter(
                 [intro_file.audio.filter('atrim', start=43),
                  auto_anchor
                  ],
                 "amix"
             ),
             v=0, a=1)
     .filter('atrim', duration=(int(float(ffmpeg.probe('news.mp3')['format']['duration'])) +
                                (2 * 45)))
     .output("out.wav", acodec='pcm_s16le', ac=2, ar=22050)
     .run(overwrite_output=True))

elif config["news"]["youtube"]["enabled"] and config["news"]["rss"]["enabled"] and not config["news"]["intro"][
    "enabled"]:
    auto_anchor = ffmpeg.input('news.mp3')
    news_file = ffmpeg.input(audio_file)
    (

        ffmpeg.concat(
            auto_anchor,
            news_file, v=0, a=1
        )
        .filter('atrim', duration=(int(float(ffmpeg.probe(audio_file)['format']['duration'])) +
                                   int(float(ffmpeg.probe('news.mp3')['format']['duration'])) +
                                   (2 * 45)))
        .output("out.wav", acodec='pcm_s16le', ac=2, ar=22050)
        .run(overwrite_output=True))

elif (not config["news"]["youtube"]["enabled"]) and config["news"]["rss"]["enabled"] and (not config["news"]["intro"][
    "enabled"]):
    auto_anchor = ffmpeg.input('news.mp3')
    (
        auto_anchor
        .filter('atrim', duration=(int(float(ffmpeg.probe('news.mp3')['format']['duration'])) +
                                   (2 * 45)))
        .output("out.wav", acodec='pcm_s16le', ac=2, ar=22050)
        .run(overwrite_output=True))

elif config["news"]["youtube"]["enabled"] and (not config["news"]["rss"]["enabled"]) and (not config["news"]["intro"][
    "enabled"]):
    news_file = ffmpeg.input(audio_file)
    (
        news_file

        .filter('atrim', duration=(int(float(ffmpeg.probe(audio_file)['format']['duration'])) +
                                   (2 * 45)))
        .output("out.wav", acodec='pcm_s16le', ac=2, ar=22050)
        .run(overwrite_output=True))
