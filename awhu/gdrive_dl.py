import requests
import sys
import IPython
import logging
from pytz import timezone
from datetime import datetime

def download_file():pass
def download_folder():pass




def gdrive_download(url,access_token=""):
    url=url.strip()
    gid=None
    ipy=IPython.get_ipython()
    try:
        if("/file/d/" in url):gid=url.split("/file/d/")[1].split("/")[0]
        elif("id=" in url):gid=url.split("id=")[1].split("/")[0].split("&")[0]
    except Exception:
        logging.warning("از این حالت پشتیبانی نمیشود فعلا آدرس گوگل درایو تونو بهم بفرستید که بفهمم چرا نمیشه")
        sys.exit()
    if(access_token!=""):
        req=requests.get(f"https://www.googleapis.com/drive/v3/files/{gid}?supportsAllDrives=true",headers={"Authorization":f"Bearer {access_token}"})
        if(req.status_code!=200):
            error_msg=req.json()['error']['message']
            logging.warning(f"{req.status_code} : {error_msg}")
            sys.exit()
        filename=req.json()["name"].replace("`","")
        ipy.run_cell(f"""!wget --header "Authorization: Bearer {access_token}"\
             "https://www.googleapis.com/drive/v3/files/{gid}?alt=media&supportsAllDrives=true" -O "{filename}" """)
    
    else:
        ipy.run_cell(f'!gdown --id "{gid}"')
    filename=""
    if(filename[-4:]in [".zip",".rar"] or filename[-3:]=="7z"):
        ipy.run_cell(f'!./7zz -y e "{filename}"')