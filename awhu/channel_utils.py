import requests
from bs4 import BeautifulSoup
import regex
import IPython
import os
import json
import sys
import time
import os
from awhu.config import Config
from telethon.sync import TelegramClient, events
from telethon.tl.types import DocumentAttributeVideo
from awhu.telegram_bot import upload, trim_id, send_msg
import asyncio
import logging
import regex
from googlesearch import search
import json


def anilist_data_ext(anilist):
    req = requests.get(anilist)
    soup = BeautifulSoup(req.text, 'html.parser')
    elements = soup.find_all("div", attrs={"class": "type"})

    def format_e(e):
        return e.text.replace("\n", " ").strip()

    def ext_element(e):
        return e.find_next_sibling()
    data = {format_e(e): format_e(ext_element(e)) for e in elements}

    q = soup.find("p", attrs={'class': "description"}).text.split('\n')[0]
    request_result = requests.get(
        f"https://translate.googleapis.com/translate_a/single?client=gtx&dt=t&sl=en&tl=fa&q={q}")
    result = [x[0] for x in json.loads(request_result.text)[0]]
    data['synopsis'] = "".join(result)
    data['original synopsis'] = q
    return data


def mal_data_ext(mal):
    req = requests.get(mal)
    soup = BeautifulSoup(req.text, 'html.parser')
    elements = soup.find_all("span", attrs={"class": "dark_text"})

    def format_s(s):
        s = s.strip()
        rep_list = [("(\s+)|(^,)|(,$)", ' '), (",+\s*(,)?", r',\1')]
        for p, r in rep_list:
            s = regex.sub(p, r, s)
        return s.strip()

    def ext_element(e):
        return ",".join(list({x.string: x for x in e.next_siblings if x.string != None}))
    data = {e.text: format_s(ext_element(e)) for e in elements}
    return data


def moreinfo_maker(send_to, trailer, info, original_synopsis=""):
    trailer_title = os.popen(
        f"youtube-dl --get-filename -f mp4 -o '%(title)s.%(ext)s' '{trailer}'").read().strip("\n")
    o = IPython.get_ipython().run_cell(f""" !youtube-dl -f 'best[height<=720]'\
    --merge-output-format "mp4"  "{trailer}"  -o '%(title)s.mp4' """)
    upload(send_to, trailer_title, info, video_mode=True)
    send_msg(send_to, original_synopsis)


def get_score(anime_name,anilist,mal):

    try:
        req = requests.get(anilist)
    except:
        anilist = search(f"{anime_name} anime anilist", num_results=1)[0]
        req = requests.get(anilist)
    soup1 = BeautifulSoup(req.text, 'html.parser')
    anilist_score = soup1.find(
        "div", text="Average Score").find_next_sibling().text.strip("%")
    season = soup1.find(
        "div", text="Season").find_next_sibling().text.strip("\n")
    format = soup1.find(
        "div", text="Format").find_next_sibling().text.strip("\n")
    if(format=="TV"):
        format="TvAnime"
    season_emojis = {"Winter": '❄️',
                     "Spring": '🍀', "Summer": '☀️', "Fall": '🍁'}
    se = season_emojis[season.split()[0]]
    
    try:
        req2 = requests.get(mal)
    except:
        mal = search(f"{anime_name} anime myanimelist", num_results=1)[0]
        if(mal.count("/")>5):
            idx=mal.rfind("/")
            mal=mal[:idx]
        req2 = requests.get(mal)
    soup2 = BeautifulSoup(req2.text, 'html.parser')
    mal_score = soup2.find("div", class_="score-label").text
    return (f"🌐 <a href={anilist}>Anilist</a>", f"🌐 <a href={mal}>MyAnimeList</a>",
            f"🎖 MyAnimeList: {mal_score}", f"🎖 AniList: {anilist_score}/100", f"{se} {season}",format)


def make_episodes_list(epi_links,chat_id):
    episodes = []
    episode_name="Episode" if(len(epi_links)<=24*3) else "Ep"
    idx=0
    while(idx<len(epi_links)):
        epi = epi_links[idx][0][0]
        epi_out=f"{episode_name} {epi}:" if(epi!="") else ""
        epi_out=f"➖ {epi_out}"
        q_list={}
        done=False
        for e in range(idx,min(idx+3,len(epi_links))):
            if(done):break
            for q in ["480","720","1080"]:
                if(q in epi_links[e][0][1]):
                    if(q in q_list):
                        done=True
                        break
                    q_list[q]=epi_links[e][1]
        for q in ["480","720","1080"]:
            if(q in q_list):
                epi_out+=f" <a href=https://t.me/{chat_id}/{q_list[q]}>{q}</a> |"
                idx+=1
        episodes.append(epi_out.strip("|"))
    return episodes


def post_maker(chat_id, anime_name, is_Bluray, links):
    bl = "[#Bluray]"if(is_Bluray)else ""
    sei = int(links["start_epi"].split("/")[-1])
    eei = int(links["end_epi"].split("/")[-1])
    epi_ids = range(sei, eei+1)
    channel_id=links["start_epi"].split("/")[-2]
    anime_name=anime_name.strip()
    mal, anilist, mal_score, anilist_score, season, format = get_score(
        anime_name,links.get("anilist",""),links.get("mal",""))
    scores = f"{anilist_score}\n{mal_score}"

    os.system(f"rm *.session*")
    asyncio.set_event_loop(asyncio.new_event_loop())
    bot = TelegramClient('bot', Config.APP_ID, Config.API_HASH).start(
        bot_token=Config.BOT_TOKEN)
    chat_id = trim_id(chat_id)

    def same_name(src, name):
        x = regex.search("\[AWHT\]([a-zA-Z!. ]*).*", name)
        return x != None and x.groups(0)[0].strip().lower() == src.lower()
    messages = bot.get_messages(channel_id, ids=list(epi_ids))
    src = regex.search("\[AWHT\]([a-zA-Z!. ]*).*",
                       messages[0].document.attributes[0].file_name).groups(0)[0].strip()

    offset = epi_ids.start
    epi_links = []
    while(offset < epi_ids.stop):
        logging.info(epi_links)
        for msg in messages:
            if msg == None or msg.document == None:
                continue
            x = msg.document.attributes[0]
            if(type(x) is DocumentAttributeVideo):
                continue
            fn = x.file_name
            if not same_name(src, fn):
                continue
            tmp = regex.search("[-Ee ]([0-9]{2,4})[ \[\(.]", fn)
            epi = tmp.groups(0)[0]if(tmp != None) else ""
            epi_links.append(((epi, fn), msg.id))
        offset += 200
        if(offset >= epi_ids.stop):
            break
        messages = bot.get_messages(
            channel_id, ids=list(range(offset, epi_ids.stop)))

    epi_links = list(dict(epi_links).items())
    epi_links.sort()
    print(epi_links)
    episodes = make_episodes_list(epi_links,channel_id)
    logging.warning(f"Total Episodes: {len(episodes)}")
    sites=f"\n{mal}\n{anilist}" if(len(episodes)<27) else ""
    episodes_out='\n'.join(episodes)

    post_header="هاردساب فارسی انیمه:"
    if(format=="Movie"):
        post_header=" هاردساب فارسی فیلم انیمه‌ای:"

    post_desc = f"✔️ {post_header}\n<b>🔥 {anime_name} {bl}\n{season}\n{scores}</b>"\
        f"\n\n📥 Download Box\n—————————\n{episodes_out}\n\n<a href={links['more_info']}>‏‏ℹ️اطلاعات بیشتر و تریلر‏</a>"\
        f"{sites}\n🎬 #{format} / @AnimWorldDL"

    if(links["poster"].strip() == ""):
        links["poster"] = "https://image-placeholder.com/images/actual-size/960x640.png"

    bot.send_file(chat_id, links["poster"], caption=post_desc, parse_mode="HTML")
