import asyncio
import sqlite3
import logging
from pathlib import Path

import config
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.types import DocumentAttributeVideo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

DB = Path("bulk_transfer.db")

def is_video(message):
    doc = getattr(message.media, "document", None)
    if not doc:
        return False
    mime = (doc.mime_type or "").lower()
    attrs = doc.attributes or []
    return mime.startswith("video/") or any(
        isinstance(a, DocumentAttributeVideo) for a in attrs
    )

async def main():
    db = sqlite3.connect(DB)
    db.execute("""
        CREATE TABLE IF NOT EXISTS copied (
            source_id INTEGER PRIMARY KEY,
            destination_id INTEGER NOT NULL
        )
    """)
    db.commit()

    client = TelegramClient(
        str(config.DOWNLOAD_DIR / config.SESSION_NAME),
        config.API_ID,
        config.API_HASH
    )

    await client.start()

    try:
        source = await client.get_entity(4334694794)
        destination = await client.get_entity(
            config.PUBLIC_VIDEO_CHANNEL
        )

        count = 0
        skipped = 0
        test_limit = 3

        async for message in client.iter_messages(
            source, reverse=True
        ):
            if not is_video(message):
                continue

            # Message 914 was already copied in the test.
            if message.id == 914:
                skipped += 1
                continue

            exists = db.execute(
                "SELECT 1 FROM copied WHERE source_id=?",
                (message.id,)
            ).fetchone()

            if exists:
                skipped += 1
                continue

            while True:
                try:
                    logging.info(
                        "Copying source video ID %s",
                        message.id
                    )

                    sent = await client.send_file(
                        destination,
                        message.media,
                        caption="🎬 XenovraStream Video",
                        supports_streaming=True,
                        force_document=False
                    )

                    db.execute(
                        "INSERT OR IGNORE INTO copied VALUES (?, ?)",
                        (message.id, sent.id)
                    )
                    db.commit()

                    count += 1
                    logging.info(
                        "Copied source %s -> destination %s",
                        message.id, sent.id
                    )
                    await asyncio.sleep(3)
                    if count >= test_limit:
                        logging.info("3-video test batch completed")
                        return
                    break

                except FloodWaitError as error:
                    logging.warning(
                        "Telegram rate limit: waiting %s seconds",
                        error.seconds
                    )
                    await asyncio.sleep(error.seconds + 5)

                except Exception:
                    logging.exception(
                        "Copy failed for source ID %s; stopping safely",
                        message.id
                    )
                    raise

        logging.info(
            "Transfer finished. Copied: %s | Skipped: %s",
            count, skipped
        )

    finally:
        db.close()
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
