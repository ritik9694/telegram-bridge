# Telegram Bridge

Python-based Telegram automation project using Telethon, SQLite and XenovraStream API.

Use only with content you own or are authorized to transfer.

## Features

- Telegram account integration
- Bulk migration workflows
- Video and PDF upload utilities
- SQLite duplicate tracking
- FloodWait handling
- Telegram listener
- XenovraStream API integration
- Environment-based configuration

## Requirements

- Python 3
- Telegram account
- Telegram API credentials
- Bot token for bot-based utilities
- Authorized channel access

## Installation

### Termux

    pkg update && pkg upgrade -y
    pkg install python git -y

Clone repository:

    git clone https://github.com/ritik9694/telegram-bridge.git
    cd telegram-bridge

Install dependencies:

    pip install -r requirements.txt

## Telegram API Setup

Get API_ID and API_HASH:

https://my.telegram.org/apps

Get BOT_TOKEN:

https://t.me/BotFather

Never publish actual credentials.

## Environment Configuration

Create local configuration:

    cp .env.example .env
    nano .env

Configure these variables:

| Variable | Purpose |
|---|---|
| API_ID | Telegram API ID |
| API_HASH | Telegram API Hash |
| SESSION_NAME | Telethon session name |
| SOURCE_CHAT_ID | Listener source channel |
| BOT_TOKEN | Telegram bot token |
| BOT_USERNAME | Bot username |
| XENOVRA_URL | XenovraStream API URL |
| XENOVRA_EMAIL | API login email |
| XENOVRA_PASSWORD | API password |
| STORAGE_ID | Storage identifier |
| DOWNLOAD_DIR | Download directory |
| MAX_CONCURRENT_DOWNLOADS | Download concurrency |
| NOTIFY_CHAT_ID | Notification chat |
| PUBLIC_VIDEO_CHANNEL | Default destination |

## Channel Mapping

| Script | Source | Destination | Database |
|---|---|---|---|
| bulk_transfer.py | 4334694794 | PUBLIC_VIDEO_CHANNEL | bulk_transfer.db |
| bulk_transfer_all.py | -1004334694794 | PUBLIC_VIDEO_CHANNEL | bulk_transfer_all.db |
| bulk_transfer_final.py | -1004334694794 | PUBLIC_VIDEO_CHANNEL | bulk_transfer_final.db |
| bulk_transfer_igiveyou.py | IGIVEYOUBATCHguys | parmar55378 | igiveyou_migration.db |
| bulk_transfer_prarhambh.py | Math_by_Abhishek_ojha_sir_2026 | prarhambh | prarhambh_migration.db |
| listener.py | SOURCE_CHAT_ID | PUBLIC_VIDEO_CHANNEL | Implementation dependent |
| upload_one.py | Local PDF | mgconceptverse | No database |
| upload_test_video.py | Local test video | @mgconceptverse | No database |

Channel identifiers reflect the current script configuration. Verify access and permissions before execution.

## Configuration Tests

    python test_config.py
    python channel_check.py
    python bot_check.py

## Listener

    python listener.py

## Bulk Transfer

Run the required workflow:

    python bulk_transfer.py
    python bulk_transfer_all.py
    python bulk_transfer_final.py
    python bulk_transfer_igiveyou.py
    python bulk_transfer_prarhambh.py

## Upload Utilities

    python upload_one.py
    python upload_test_video.py

Check local file paths and bot permissions before running.

## Database Files

- bulk_transfer.db
- bulk_transfer_all.db
- bulk_transfer_final.db
- igiveyou_migration.db
- prarhambh_migration.db

SQLite databases maintain migration records. Keep local backups to preserve duplicate tracking.

## Telegram Sessions

Default session name: xenovra_session

Session files contain sensitive authentication information. Never upload or share them.

## Troubleshooting

- Missing configuration: Check the .env file.
- FloodWaitError: Respect Telegram's specified waiting period.
- Channel access error: Verify account permissions.
- Bot permission error: Check destination bot permissions.
- Duplicate messages: Check the corresponding SQLite database.

## Security

Never upload:

- .env
- Telegram session files
- API_HASH
- BOT_TOKEN
- Passwords
- Private databases
- Downloaded media

Rotate credentials if exposed.

## GitHub Updates

    git status
    git add .
    git commit -m "Update Telegram Bridge"
    git push

Always inspect staged files before committing.

## Repository

https://github.com/ritik9694/telegram-bridge

Branch: main
