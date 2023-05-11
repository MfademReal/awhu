import os
import IPython
import random
import gdown
early_setup="""
chmod +x 7zz
chmod +x ffmpeg
apt install mediainfo
apt install python3-libtorrent
7z x All_Needy_Fonts.7z -o/usr/share/fonts/ -y
rm /usr/share/fonts/pHalls* 
fc-cache -f 
git clone https://github.com/awht-team/fonts.git
cd "fonts" && cp *.ttf *.TTF *.otf *.OTF *.ttc *.TTC /usr/share/fonts/ 
touch /content/INSTALLED
"""

logger_code="""
import logging
import sys
logging.basicConfig(filename="debug.log",
                            filemode='a',
                            format='%(asctime)s: %(message)s',
                            datefmt='%y/%m/%d  %H:%M:%S',
                            level=logging.INFO)

console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.WARNING)
logging.getLogger('').addHandler(console)
"""
fontpack_gdrive_ids=[
    "1uORS6zePXbR80NDN4B5zmN3-0t7ONyas",
    "1ouDjHGr93x1Il0DFjmK7eNaLHpjHRWK_",
    "1JUXQgXapuo82qGB0Q0eJAtGrKi_ZvgfZ",
    "1_hwDcfgFpUD1nslLbLL1UdIw_T-5MHjm",
    "1A50s-Ag5S0B2vl4Z9t9_db_khNK46lh7",
    "1N5hC8yBnWuLEMSYYx7Xl9pP--X8jBzAX",
    "1oJ5MP-6uLo_EFmjccSZRhPWxveVV8mT4",
    "1ECuRZqHzzsjtBwYgjMrtL4YqLL9FByXP",
    "1TjNrwDYF6Ezd3OLfSHpJdc75trRHPurV",
    "1S_p0--mTncKLjiI7Eg8Z9nbLiVt3cWqr"]


def install_essentials():
    from awhu.config import Config      
    os.system(f"git clone https://github.com/MfademReal/aw_stuff/* . && rm -r aw_stuff")
    while(not os.path.exists("All_Needy_Fonts.7z")):
        gd=random.choice(fontpack_gdrive_ids)
        # os.system(f"gdown --id {gd}")
        gdown.download(
            f"https://drive.google.com/uc?export=download&confirm=pbef&id={gd}",
            "All_Needy_Fonts.7z"
        )

    with open("/usr/lib/python3.8/logging/__init__.py", 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write("from pytz import timezone\nfrom datetime import datetime\n" + content)
    with open("/content/early_setup.sh","w") as f:
        f.write(early_setup)
    os.system("chmod +x /content/early_setup.sh")
    o=IPython.get_ipython().run_cell("!./early_setup.sh")
    IPython.display.clear_output()
    exec(logger_code)
    with open("/root/.ipython/profile_default/startup/startup.py","a") as f:
        f.write(logger_code)
    if(os.path.exists("All_Needy_Fonts.7z")):
        os.system("rm All_Needy_Fonts.7z")
    else: 
        print("پک فونت ها نصب نشد به ادمینا پیام بدید لطفا")



