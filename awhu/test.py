import asyncio
from telethon.sync import TelegramClient
apiHash = "7fd33cdfb5bf201e33e98ea27b682389"
app_id = "17687296"
botToken = "5225075398:AAHlPZY7cJGKDBDLxGgfcqk5M9gixTK9KFk"

bot = TelegramClient('bot',app_id, apiHash).start(bot_token=botToken)
bot.send_file("@iMr_Fun","/home/mrfun/Downloads/texture/test.torrent")