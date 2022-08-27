import telegram
import os

class Config(object):
    DORY_BOT_TOKEN = "5756117311:AAEMsDXEBQE22Xv6gTNrcjXKpY1AJaHdNMQ" 
    dorybot = telegram.Bot(token=DORY_BOT_TOKEN)
    BOT_TOKEN=os.environ["BOT_TOKEN"]
    APP_ID=int(os.environ["APP_ID"])
    API_HASH=os.environ["API_HASH"]
    AWHT_ID=os.environ["AWHT_ID"]
    AWHT_TOKEN=os.environ["َAWHT_TOKEN"]
    TG_ID=os.environ["TG_ID"]
    LOGGER_CHANNEL={1:-1001606884080,2:-1001606884080,"bug":-1001606884080}
    
class FFmpegConfig(object):
    crf=25
    preset="faster"
    

