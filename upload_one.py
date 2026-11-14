import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv(".env")

PDF = Path.home() / "storage/downloads/MG_Concept/Speedverse/Phase_1/CLASS-1 SPEED CALCULATION + OPTION TEST.pdf"
CHANNEL = "mgconceptverse"

async def main():
    if not PDF.is_file():
        raise FileNotFoundError(PDF)

    client = TelegramClient(
        "bot_check_temp",
        int(os.environ["API_ID"]),
        os.environ["API_HASH"]
    )

    await client.start(bot_token=os.environ["BOT_TOKEN"])
    try:
        channel = await client.get_entity(CHANNEL)
        result = await client.send_file(
            channel,
            str(PDF),
            caption=PDF.stem,
            force_document=True
        )
        print("UPLOAD SUCCESS")
        print("Message ID:", result.id)
        print("Filename:", PDF.name)
    finally:
        await client.disconnect()

asyncio.run(main())
