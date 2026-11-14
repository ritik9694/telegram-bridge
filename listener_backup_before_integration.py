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
    document = getattr(message.media, "document", None)

    if not document:
        return False

    mime = (document.mime_type or "").lower()

    video_attribute = any(
        isinstance(attr, DocumentAttributeVideo)
        for attr in (document.attributes or [])
    )

    filename = (message.file.name or "").lower()
    video_extension = filename.endswith(
        (".mp4", ".mkv", ".mov", ".webm", ".avi")
    )

    return (
        mime.startswith("video/")
        or video_attribute
        or video_extension
    )


@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handle_new_message(event):
    message = event.message

    if not is_video(message):
        return

    size = message.file.size or 0
    filename = message.file.name or f"video_{message.id}.mp4"
    safe_name = f"{message.id}_{filename}"

    output_path = config.DOWNLOAD_DIR / safe_name

    if output_path.exists():
        logging.info("Already downloaded: %s", safe_name)
        return

    logging.info("New video detected: %s", filename)
    logging.info("Size: %.2f MB", size / (1024 * 1024))

    try:
        await client.download_media(message, file=str(output_path))

        logging.info("Download completed: %s", output_path)
    except Exception:
        logging.exception("Video download failed")


async def main():
    if not SOURCE_CHANNEL:
        raise ValueError("SOURCE_CHAT_ID missing in .env")

    await client.start()

    me = await client.get_me()
    logging.info("Connected as: %s", me.first_name)
    logging.info("Monitoring: %s", SOURCE_CHANNEL)
    logging.info("Automatic download is active!")

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
