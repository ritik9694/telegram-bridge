import asyncio
import logging
import re
import httpx

from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeVideo

import config
from xenovra_api import XenovraAPI

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
semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_DOWNLOADS)


def is_video(message):
    document = getattr(message.media, "document", None)
    if not document:
        return False

    mime = (document.mime_type or "").lower()
    attrs = document.attributes or []

    video_attr = any(
        isinstance(attr, DocumentAttributeVideo) for attr in attrs
    )

    filename = (message.file.name or "").lower()
    extension = filename.endswith(
        (".mp4", ".mkv", ".mov", ".webm", ".avi")
    )

    return mime.startswith("video/") or video_attr or extension


async def notify(text):
    if not config.NOTIFY_CHAT_ID or not config.BOT_TOKEN:
        logging.warning("Notification configuration missing")
        return

    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"

    async with httpx.AsyncClient(timeout=30) as http:
        response = await http.post(
            url,
            json={
                "chat_id": config.NOTIFY_CHAT_ID,
                "text": text,
                "disable_web_page_preview": False
            }
        )
        response.raise_for_status()


async def wait_for_processing(api, video):
    video_id = video["id"]

    for attempt in range(5760):
        await asyncio.sleep(15)

        response = await api.client.get(
            f"{api.base_url}/api/videos/{video_id}"
        )
        response.raise_for_status()

        current = response.json()
        status = current.get("status", "")

        logging.info(
            "Video %s processing status: %s",
            video_id,
            status
        )

        if status == "ready":
            return current

        if status == "failed":
            raise RuntimeError(
                current.get("error") or "Video processing failed"
            )

    raise TimeoutError("Processing did not finish within 24 hours")


async def handle_video(message):
    async with semaphore:
        filename = message.file.name or f"video_{message.id}.mp4"
        filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

        safe_name = f"{message.id}_{filename}"
        output_path = config.DOWNLOAD_DIR / safe_name

        marker = config.DOWNLOAD_DIR / f"{message.id}.submitted"
        public_marker = config.DOWNLOAD_DIR / f"{message.id}.public_uploaded"

        if marker.exists():
            logging.info("XenovraStream upload already accepted; checking public upload")

        api = XenovraAPI()

        try:
            logging.info("New video: %s", filename)

            if not output_path.exists():
                await client.download_media(
                    message,
                    file=str(output_path)
                )

            logging.info("Download completed: %s", output_path)

            if not public_marker.exists():
                logging.info("Uploading original MP4 to public channel")
                await client.send_file(
                    config.PUBLIC_VIDEO_CHANNEL,
                    str(output_path),
                    caption=f"🎬 {filename}",
                    supports_streaming=True,
                    force_document=False
                )
                public_marker.write_text(str(message.id))
                logging.info("Original MP4 uploaded successfully")
            else:
                logging.info("MP4 already uploaded to public channel")

            await api.login()

            if marker.exists():
                video_id = marker.read_text().strip()
                response = await api.client.get(
                    f"{api.base_url}/api/videos/{video_id}"
                )
                response.raise_for_status()
                result = response.json()
                logging.info("Reusing existing XenovraStream video")
            else:
                result = await api.upload_video(output_path, filename)
                marker.write_text(str(result["id"]))

            logging.info("XenovraStream upload accepted: %s", result)

            await notify(
                f"📤 Video uploaded to XenovraStream\n"
                f"Title: {filename}\n"
                f"Status: Processing"
            )

            ready_video = await wait_for_processing(api, result)

            public_id = ready_video["public_id"]

            player_link = f"{api.base_url}/s/{public_id}"
            hls_link = f"{api.base_url}/s/{public_id}.m3u8"

            await notify(
                f"✅ Video processing completed!\n\n"
                f"🎬 {filename}\n\n"
                f"▶ Player: {player_link}\n"
                f"📺 HLS: {hls_link}"
            )

            output_path.unlink(missing_ok=True)

            logging.info("Completed successfully: %s", filename)

        except Exception as error:
            logging.exception("Video processing failed")
            try:
                await notify(
                    f"❌ Video processing failed\n"
                    f"File: {filename}\n"
                    f"Error: {str(error)[:500]}"
                )
            except Exception:
                logging.exception("Failure notification could not be sent")

        finally:
            await api.close()


@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handle_new_message(event):
    message = event.message

    if not is_video(message):
        return

    asyncio.create_task(handle_video(message))


async def main():
    if not SOURCE_CHANNEL:
        raise ValueError("SOURCE_CHAT_ID missing")

    if not config.NOTIFY_CHAT_ID:
        raise ValueError("NOTIFY_CHAT_ID missing")

    await client.start()

    me = await client.get_me()

    logging.info("Connected as: %s", me.first_name)
    logging.info("Monitoring channel: %s", SOURCE_CHANNEL)
    logging.info("Automatic download and upload enabled")

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())

