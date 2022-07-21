import time
import os
import sys
import re
import regex
import requests
from subprocess import Popen, PIPE, STDOUT
from awhu.subtitle import Subtitle
from awhu.hardsub_logger import *
import IPython
from threading import Thread
import logging

def auto_detect_source(anime_name,episode_number):
    possible_anime_names = [anime_name, anime_name.replace(" ", "_"), anime_name.replace(" ", "-"),
                        anime_name.replace(" ", "."), anime_name.split()[0], ""]

    for an in possible_anime_names:
        tmp = os.popen(
          f"(find . -name '*.mkv' & find . -name '*.mp4') | grep -i \"{an}\" | grep \"{episode_number}\" | grep -v 'AWHT'").read().split("\n")
        if(len(tmp[0].strip()) != 0): break
    source = tmp[0]
    logging.warning(f"ِDetected Source: {source}")
    return source


def auto_detect_subtitle(anime_name,episode_number):
    possible_anime_names = [anime_name, anime_name.replace(" ", "_"), anime_name.replace(" ", "-"),
                        anime_name.replace(" ", "."), anime_name.split()[0], ""]

    for an in possible_anime_names:
        tmp = os.popen(
          f"find . -name '*.ass' | grep -i \"{an}\" | grep \"{episode_number}\" ").read().split("\n")
        if(len(tmp[0].strip()) != 0): break
    subtitle = tmp[0]
    logging.warning(f"ِDetected Subtitle: {subtitle}")
    return subtitle


def hardsub_anime(hconfig:dict):

    fonts_ext="*.ttf *.TTF *.otf *.OTF *.ttc *.TTC"
    os.system(f"mv {fonts_ext} fonts")
    os.system(f"cd fonts && git pull origin && cp {fonts_ext} /usr/share/fonts/ ")

    hconf=hconfig.copy()
    hconf["encoder"]=hconf.get("encoder","libx264")
    x264_extra_configs=""
    if(hconf["encoder"]=="libx264"):
        x264_extra_configs=" -tune animation -deblock 0:0 -flags +loop"
    print(f"x264 configs: {x264_extra_configs}")
    hconf["filter"]=f",{hconf['filter']}" if hconf.get("filter","").strip()!="" else ""
    for k,v in hconf.items():
        if(type(v)==str):
            hconf[k]=v.strip()
    is_old="_old" if (hconf["subtitle"][-1]=="$")else ""
    hconf["subtitle"]=hconf["subtitle"].strip("$")
    no_sub= hconf["subtitle"].strip()=="-"
    if(hconf["source"] == "auto"):
        hconf["source"] = auto_detect_source(hconf["anime_name"],hconf["episode_number"])

    if(not no_sub and hconf["subtitle"] == "auto"):
        hconf["subtitle"] = auto_detect_subtitle(hconf["anime_name"],hconf["episode_number"])

   
    if(not no_sub and hconf["subtitle"][-4:]!=".ass"):
        hconf["subtitle"]=f"{hconf['subtitle']}.ass"

    if(not no_sub and not os.path.exists(hconf["subtitle"])):  
        logging.warning("زیرنویس رو پیدا نکردم مطمئنید آپلودش کردید؟")
        return

    if(not os.path.exists(hconf["source"])):  
        logging.warning("فایلی که میخواید هاردساب کنید رو پیدا نکردم مطئنید دانلود شده؟")
        return
    if(len(hconf["output_name"])>64):  
        logging.warning("اسم انیمه خیلی طولانیه، کوتاه ترش کنید")
        return
    ffmpeg_data= Popen(f"./ffmpeg -i \"{hconf['source']}\"", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().decode(encoding= 'unicode_escape')
    audio_list=[x.groups() for x in regex.finditer(
            "Stream #0:([0-9])\(([a-z]{2,3})\): Audio:", ffmpeg_data)]
    audio_dict={a:int(ai)-1 for ai,a in audio_list}
    if(len(audio_dict)<2):
        audio_tmp=[x.groups() for x in regex.finditer(
            "Stream #0:([0-9]): Audio:(?s)(.+?)(?=Stream)", ffmpeg_data)]
        audio_list=[(i,regex.sub("(?s).*English(?s).*","eng",regex.sub("(?s).*Japanese(?s).*","jpn",lang,regex.I),regex.I)) for i,lang in audio_tmp]
        audio_dict={a:int(ai)-1 for ai,a in audio_list}
            
    audio_id=0
    try:
        if(hconf["audio"]=="English"):
            audio_id=audio_dict["eng"]
        elif(hconf["audio"]=="Japanese"):
            audio_id=audio_dict["jpn"]
        elif("Track" in hconf["audio"] ):
            audio_id=int(hconf["audio"].split("Track")[1])-1
    except:
        logging.warning("\n\n\n\nزبانی که انتخاب کردید یافت نشد صدای دیفالت رو انتخاب میکنیم")
       
        time.sleep(2)
    which_audio=f"-map a:{audio_id}" if(hconf["audio"]!="Dual") else"-map a"
    
    if(not no_sub):
        sub=Subtitle(hconf["subtitle"])
        sub_log=sub.nonb_farsifont_bug_fixer()
        logging.warning(sub_log)
        sub_log2=sub.numbers_bug_fixer()
        logging.warning(sub_log2)
        sub.export("anime_sub.ass")

    # resolution
    scale=f"trunc(oh*a/2)*2:{hconf['resolution']}"
    hd_resolution={"480":852,"720":1280,"1080":1920}
    if(hconf["is_movie"]):
        scale=f"{hd_resolution[hconf['resolution']]}:trunc(ow/a/2)*2"
    

    os.rename(hconf["source"],hconf["source"].replace("`",""))
    begin = time.time()
    if("movie" in hconf["filter"]):
        return IPython.get_ipython().run_cell(f"""!ffmpeg -y -i "{hconf["source"]}" \
        -map v {which_audio}? \
        -max_muxing_queue_size 1024 \
        -vf "scale={scale},ass=anime_sub.ass" \
        -c:a libfdk_aac -b:a 128k -ac 2 \
        -c:v {hconf["encoder"]} -preset "{hconf["preset"]}" -crf "{hconf["crf"]}" -pix_fmt yuv420p -tune film\
        "{hconf["output_name"]}" -progress - -nostats""")


    o=IPython.get_ipython().run_cell(f"""!ffmpeg -y -i "{hconf["source"]}" \
    -map v {which_audio}? {("","-map s? -map t? -c:s copy")[no_sub]}\
    -max_muxing_queue_size 1024 \
    -vf "scale={scale},{("ass=anime_sub.ass,","")[no_sub]}ass=AWHT_New_WaterMark{is_old}.ass{hconf["filter"]}" \
    -c:a libfdk_aac -b:a 128k -ac 2 \
    -c:v {hconf["encoder"]} -preset "{hconf["preset"]}" -crf "{hconf["crf"]}" {x264_extra_configs} \
    "{hconf["output_name"]}" -progress - -nostats""")



    end = time.time()
    hconf["elapsed time"]=f"{int((end-begin)//60)} min : {int((end-begin)%60)} sec"
    h_info=get_hardsub_info(hconf,("hardsub","encode")[no_sub])
    disable_log=hconf.get("disable_log",False)
    if(not disable_log):
        send_log_public(h_info,hconf["level"])

    # Non-Direct Upload
   # if(Config.AWHT_ID in ["Shiroyasha","NOT85","Phantom"]):
        payload= {'chat_id':Config.TG_ID}
        file=hconf["output_name"]
        files={'file': (file, open(file, 'rb')),}
        begin = time.time()
        x=requests.post("https://colab-hs.herokuapp.com/upload",data=payload,files=files)
        end = time.time()
        print(f"{int((end-begin)//60)} min : {int((end-begin)%60)} sec")
