import asyncio
import logging

from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeVideo

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

client = TelegramClient(
    str(config.DOWNLOAD_DIR / config.SESSION_NAME),
    config.API_ID,
    config.API_HASH
)

SOURCE_CHANNEL = config.SOURCE_CHAT_ID


def is_video(message):
    if not message or not message.media:
        return False

    document = getattr(message.media, "document", None)

    if not document:
        return False

    mime_type = getattr(document, "mime_type", "") or ""

    has_video_attribute = any(
        isinstance(attr, DocumentAttributeVideo)
        for attr in (document.attributes or [])
    )

    return mime_type.startswith("video/") or has_video_attribute


@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handle_new_message(event):
    message = event.message

    if not is_video(message):
        return

    logging.info("New video detected!")
    logging.info("Channel: %s", event.chat_id)
    logging.info("Message ID: %s", message.id)
    logging.info("File size: %s bytes", message.file.size)


async def main():
    if not SOURCE_CHANNEL:
        raise ValueError("SOURCE_CHAT_ID is missing in .env")

    await client.start()

    me = await client.get_me()

    logging.info("Telegram connected successfully!")
    logging.info("Logged in as: %s", me.first_name)
    logging.info("Monitoring channel: %s", SOURCE_CHANNEL)

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
