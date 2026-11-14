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
    format="%(asctime)s | %(message)s"
)

DB = Path("bulk_transfer_all.db")
SOURCE_ID = -1004334694794
TEST_COPIES = {
    914: 5,
    26: 6,
    29: 7,
    32: 8,
}


def media_type(message):
    doc = getattr(message.media, "document", None)
    if not doc:
        return None

    mime = (doc.mime_type or "").lower()
    name = (message.file.name or "").lower()

    if mime == "application/pdf" or name.endswith(".pdf"):
        return "pdf"

    if mime.startswith("video/") or any(
        isinstance(a, DocumentAttributeVideo)
        for a in (doc.attributes or [])
    ):
        return "video"

    return None


async def main():
    db = sqlite3.connect(DB)

    db.execute("""
        CREATE TABLE IF NOT EXISTS copied (
            source_id INTEGER PRIMARY KEY,
            destination_id INTEGER NOT NULL
        )
    """)

    db.executemany(
        "INSERT OR IGNORE INTO copied VALUES (?, ?)",
        TEST_COPIES.items()
    )
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
            old = db.execute(
                "SELECT 1 FROM copied WHERE source_id=?",
                (msg.id,)
            ).fetchone()

            if old:
                skipped += 1
                continue

            kind = media_type(msg)
            text = msg.message or ""

            if not kind and not text:
                skipped += 1
                continue

            try:
                while True:
                    try:
                        if kind:
                            if len(text) > 1024:
                                if text:
                                    await client.send_message(
                                        destination,
                                        text,
                                        parse_mode=None
                                    )
                                sent = await client.send_file(
                                    destination,
                                    msg.media,
                                    supports_streaming=(kind == "video"),
                                    force_document=(kind == "pdf"),
                                    parse_mode=None
                                )
                            else:
                                sent = await client.send_file(
                                    destination,
                                    msg.media,
                                    caption=text or None,
                                    supports_streaming=(kind == "video"),
                                    force_document=(kind == "pdf"),
                                    parse_mode=None
                                )
                        else:
                            sent = await client.send_message(
                                destination,
                                text,
                                parse_mode=None
                            )

                        db.execute(
                            "INSERT INTO copied VALUES (?, ?)",
                            (msg.id, sent.id)
                        )
                        db.commit()

                        copied += 1
                        logging.info(
                            "Copied source %s (%s) -> destination %s",
                            msg.id, kind or "TEXT", sent.id
                        )
                        await asyncio.sleep(3)
                        if copied >= 3:
                            logging.info("TEST batch complete")
                            return
                        break

                    except FloodWaitError as e:
                        logging.warning(
                            "Rate limit: waiting %s seconds",
                            e.seconds
                        )
                        await asyncio.sleep(e.seconds + 5)

            except Exception:
                logging.exception(
                    "Stopped safely at source ID %s",
                    msg.id
                )
                raise

        logging.info(
            "Migration finished. Copied=%s Skipped=%s",
            copied, skipped
        )

    finally:
        db.close()
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

