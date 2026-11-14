import asyncio, os
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv(".env")

async def main():
    client = TelegramClient(
        "bot_check_temp",
        int(os.getenv("API_ID")),
        os.getenv("API_HASH")
    )
    await client.start(bot_token=os.getenv("BOT_TOKEN"))
    me = await client.get_me()
    print("Bot connected:", me.username)
    print("Bot ID:", me.id)
    await client.disconnect()

asyncio.run(main())
