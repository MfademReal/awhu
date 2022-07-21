import os
import regex
from telegram.constants import PARSEMODE_HTML,PARSEMODE_MARKDOWN
from awhu.config import Config
import sys
import logging
 

def search(rgx:str,data,flags=0):
    tmp = regex.search(
        rgx, data, flags=flags)
    return tmp.groups()[0] if(tmp!=None) else "NS"
    
def get_mediainfo(media):
    media_data = os.popen(f"mediainfo \"{media}\"").read()
    media_info = {}

    media_info["file size"]=search("^File size\s+: (.*)",media_data,regex.MULTILINE)

    media_info["duration"] = search(
        "^Duration \s+: (.*)", media_data, flags=regex.MULTILINE)

    media_info["overall bitrate"] = search(
        "^Overall bit rate\s+: (.*)", media_data, flags=regex.MULTILINE)

    media_info["width"] = search(
        "^Width\s+: ([0-9 ]*)", media_data, flags=regex.MULTILINE).replace(" ","")

    media_info["height"] = search(
        "^Height\s+: ([0-9 ]+)", media_data, flags=regex.MULTILINE).replace(" ","")

    media_info["bit depth"] = search(
        "^Bit depth\s+: (.*)", media_data, flags=regex.MULTILINE)

    media_info["writing library"]=search(
        "Video(?s).*Writing library\s+: ([^(\n\s)]*).*Audio", media_data)
    return media_info


def get_hardsub_info(hconf,mode):
    source=hconf["source"]
    output=hconf["output_name"]
    source_info = get_mediainfo(source)
    output_info = get_mediainfo(output)

    return f"""🎬<b>Source INFO:</b>
        <b>Name</b>: {source.split("/")[-1]}
        <b>Size</b>: {source_info["file size"]}
        <b>Duration</b>: {source_info["duration"]}
        <b>Overall Bit Rate</b>: {source_info["overall bitrate"]}
        <b>Encode Config</b>:{source_info["writing library"]} - {source_info["bit depth"] }- {source_info["width"]}×{source_info["height"]}
<b>Hardsubbed File INFO:</b>
        <b>User</b>: #{Config.AWHT_ID}
        <b>Telegram_ID</b>: @{Config.TG_ID}
        <b>Name</b>: {output}
        <b>Size</b>: {output_info["file size"]}
        <b>Duration</b>: {output_info["duration"]}
        <b>Overall Bit Rate</b>: {output_info["overall bitrate"]}
        <b>Preset</b>: #{hconf["preset"]}
        <b>crf</b>: {hconf["crf"]}
        <b>Elapsed Time</b>: {hconf["elapsed time"]}
#{mode}
#{hconf["anime_name"].replace(" ","_")}_{hconf["episode_number"]}
#{hconf["anime_name"].replace(" ","_")}_{hconf["resolution"]}_{hconf["episode_number"]}"""

   


def send_log_public(log_info,level):
    Config.dorybot.send_message(chat_id=Config.LOGGER_CHANNEL[level], text=log_info,
                        parse_mode=PARSEMODE_HTML)

def send_log_private(log_info,chat_id=Config.TG_ID):
    Config.dorybot.send_message(chat_id=chat_id, text=log_info,
                        parse_mode=PARSEMODE_HTML)


def report_bug(title,desc):
    Config.dorybot.send_document(chat_id=Config.LOGGER_CHANNEL["bug"],document=open("debug.log"),
    filename=f"debug_{Config.TG_ID}.log",caption=f"**{title}**\n{desc}\n**Reported By @{Config.TG_ID}**",
    parse_mode=PARSEMODE_MARKDOWN)