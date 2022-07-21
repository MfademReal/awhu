import sys
import os
import re 
import regex
from googlesearch import search
from urllib import parse
import requests
from bs4 import BeautifulSoup
import time
import json
font_sites=["https://dl.dafont.com/dl/?f=***","https://www.fontsquirrel.com/fonts/download/***"
            ,"https://www.wfonts.com/font/***","https://www.fontmirror.com/***"]
fonts_ext="*.ttf *.TTF *.otf *.OTF *.ttc *.TTC"


def unzip(zipfile):
    os.system(f"./7zz -y e \"{zipfile}\"  -o/fonts {fonts_ext} -r ")

def download_anime_attachments():
  req=requests.get(f"https://mirror.animetosho.org/search?q={anime_name.replace(' ','+')}")
  soup = BeautifulSoup(req.text, 'html.parser')
  d_ha=soup.find_all("div",{"class":"link"})
  d_ha=[d for d in d_ha if("NZB" in d.find_next_sibling("div").__str__())][:5]
  for d in d_ha:
    req_d=requests.get(d.a["href"])
    soup_d = BeautifulSoup(req_d.text, 'html.parser')
    tmp=soup_d.find("a", text="All Attachments")
    if(tmp==None):continue
    os.system(f"wget -P Animetosho \"{tmp['href']}\"")
    unzip("Animetosho/*.7z")


def check_font(font):
    os.system(f"cd fonts && cp {fonts_ext} /usr/share/fonts/ ")
    fontr=font.replace("-","\-")
    tmp=os.popen(f"fc-match \"{fontr}\" ").read()
    if(tmp==""):return False
    tmp2=list(filter(None, tmp.split("\"")))
    res=[tmp2[1].lower(),"".join(tmp2[1:]).lower()]
    res.append(res[1].replace(" ","-"))
    return (font.lower() in res) or (True in [font.split()[0].lower() in r for r in res])
