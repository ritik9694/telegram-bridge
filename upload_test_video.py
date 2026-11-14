import asyncio
from pathlib import Path
from telethon import TelegramClient
from config import API_ID, API_HASH, BOT_TOKEN

VIDEO = Path(__file__).parent / "test_media" / "telegram_test.mp4"
CHANNEL = "@mgconceptverse"

async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN missing in telegram_bridge/.env")

    if not VIDEO.is_file():
        raise FileNotFoundError(VIDEO)

    client = TelegramClient(
        str(Path(__file__).parent / "speedverse_test_bot"),
        API_ID,
        API_HASH
    )

    try:
        await client.start(bot_token=BOT_TOKEN)
        channel = await client.get_entity(CHANNEL)

        result = await client.send_file(
            channel,
            str(VIDEO),
            caption="XenovraStream Telegram upload test",
            supports_streaming=True
        )

        print("UPLOAD SUCCESS")
        print("Message ID:", result.id)

    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
