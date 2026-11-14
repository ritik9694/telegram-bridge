import asyncio, os
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantRequest

load_dotenv(".env")

async def main():
    client = TelegramClient(
        "bot_check_temp",
        int(os.getenv("API_ID")),
        os.getenv("API_HASH")
    )
    await client.start(bot_token=os.getenv("BOT_TOKEN"))
    try:
        channel = await client.get_entity("mgconceptverse")
        result = await client(GetParticipantRequest(channel, await client.get_me()))
        p = result.participant
        print("Channel:", channel.title)
        print("Bot is admin:", type(p).__name__ == "ChannelParticipantAdmin")
        if hasattr(p, "admin_rights"):
            print("Post messages permission:", p.admin_rights.post_messages)
    except Exception as e:
        print("Check failed:", type(e).__name__, str(e)[:250])
    await client.disconnect()

asyncio.run(main())
