import asyncio
import logging
import config
import listener

logging.basicConfig(level=logging.INFO)

async def main():
    client = listener.client

    # Disable live handler during historical import
    client.remove_event_handler(listener.handle_new_message)

    await client.start()

    count = 0
    skipped = 0

    try:
        async for message in client.iter_messages(
            config.SOURCE_CHAT_ID,
            reverse=True
        ):
            if not listener.is_video(message):
                continue

            marker = config.DOWNLOAD_DIR / f"{message.id}.submitted"
            public_marker = config.DOWNLOAD_DIR / f"{message.id}.public_uploaded"

            if marker.exists() and public_marker.exists():
                logging.info("Skipping completed video ID %s", message.id)
                skipped += 1
                continue

            logging.info("Importing old video ID %s", message.id)
            await listener.handle_video(message)
            count += 1

        logging.info("Bulk import finished. Processed: %s, skipped: %s", count, skipped)

    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
