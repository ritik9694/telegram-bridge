import asyncio
import sqlite3
import logging
from pathlib import Path

import config
from telethon import TelegramClient
from telethon.errors import FloodWaitError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)

SOURCE_ID = -1004334694794
DB = Path("bulk_transfer_final.db")


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
        source = await client.get_entity(SOURCE_ID)
        destination = await client.get_entity(
            config.PUBLIC_VIDEO_CHANNEL
        )

        copied = 0
        skipped = 0

        async for msg in client.iter_messages(
            source, reverse=True
        ):
            if msg.action or (not msg.message and not msg.media):
                skipped += 1
                continue

            exists = db.execute(
                "SELECT 1 FROM copied WHERE source_id=?",
                (msg.id,)
            ).fetchone()

            if exists:
                skipped += 1
                continue

            while True:
                try:
                    sent = await client.forward_messages(
                        destination,
                        msg,
                        from_peer=source,
                        drop_author=True
                    )

                    if isinstance(sent, list):
                        sent = sent[0]

                    db.execute(
                        "INSERT INTO copied VALUES (?, ?)",
                        (msg.id, sent.id)
                    )
                    db.commit()

                    copied += 1
                    logging.info(
                        "Copied source %s -> destination %s",
                        msg.id, sent.id
                    )

                    await asyncio.sleep(3)

                    break

                except FloodWaitError as e:
                    logging.warning(
                        "Waiting %s seconds", e.seconds
                    )
                    await asyncio.sleep(e.seconds + 5)

                except Exception:
                    logging.exception(
                        "Failed at source ID %s", msg.id
                    )
                    raise

        logging.info(
            "Finished. Copied=%s Skipped=%s",
            copied, skipped
        )

    finally:
        db.close()
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
