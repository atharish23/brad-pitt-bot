import os
import time
import asyncio
from threading import Thread
from flask import Flask
from pyrogram import Client, filters

# Render Health Check Fix
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is Live and Running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# Credentials
API_ID = 29884680
API_HASH = "ff4b89a18ed81b27f406d719c580689f"
BOT_TOKEN = "8971531788:AAHV2d8P23EhY0uoRI4xtkNI82pSPHMVxKM"
CHANNEL_TAG = "@Brad_Pitt_Movies"

app = Client(
    "BradPittBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

user_thumbs = {}

async def progress_bar(current, total, status_msg, start_time, action_type):
    now = time.time()
    diff = now - start_time
    if round(diff % 3) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff if diff > 0 else 0
        elapsed_time = round(diff)
        eta = round((total - current) / speed) if speed > 0 else 0

        progress = "".join(["■" for _ in range(int(percentage // 10))]) + "".join(
            ["□" for _ in range(10 - int(percentage // 10))]
        )

        status_text = (
            f"**{action_type}...**\n\n"
            f"[{progress}] {percentage:.1f}%\n\n"
            f"**Processed:** {current / (1024 * 1024):.2f} MB / {total / (1024 * 1024):.2f} MB\n"
            f"**Speed:** {speed / (1024 * 1024):.2f} MB/s\n"
            f"**ETA:** {eta}s | **Elapsed:** {elapsed_time}s"
        )
        try:
            await status_msg.edit_text(status_text)
        except Exception:
            pass

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply_text(
        f"Hello {message.from_user.first_name}! 👋\n\n"
        "Send me any video/document, and I will rename it and add **@Brad_Pitt_Movies** tag.\n"
        "You can also send a photo to set a custom thumbnail!"
    )

@app.on_message(filters.photo)
async def set_thumbnail(client, message):
    user_id = message.from_user.id
    photo_path = await message.download()
    user_thumbs[user_id] = photo_path
    await message.reply_text("✅ **Custom Thumbnail Saved Successfully!**")

@app.on_message(filters.command("delthumb"))
async def delete_thumbnail(client, message):
    user_id = message.from_user.id
    if user_id in user_thumbs:
        if os.path.exists(user_thumbs[user_id]):
            os.remove(user_thumbs[user_id])
        del user_thumbs[user_id]
        await message.reply_text("🗑️ **Custom Thumbnail Deleted!**")
    else:
        await message.reply_text("❌ **No custom thumbnail found.**")

@app.on_message(filters.document | filters.video)
async def rename_handler(client, message):
    msg = await message.reply_text("⏳ **Downloading file...**")
    user_id = message.from_user.id
    start_time = time.time()

    file_name = message.document.file_name if message.document else message.video.file_name
    if not file_name:
        file_name = "video.mp4"

    name, ext = os.path.splitext(file_name)
    new_name = f"{name} {CHANNEL_TAG}{ext}"

    file_path = None
    try:
        file_path = await client.download_media(
            message,
            progress=progress_bar,
            progress_args=(msg, start_time, "Downloading"),
        )

        await msg.edit_text("⏳ **Uploading file...**")
        upload_start = time.time()

        thumb = user_thumbs.get(user_id, None)
        caption = f"**{new_name}**\n\nMaintained by: {CHANNEL_TAG}"

        if message.video:
            await client.send_video(
                chat_id=message.chat.id,
                video=file_path,
                thumb=thumb if (thumb and os.path.exists(thumb)) else None,
                caption=caption,
                file_name=new_name,
                progress=progress_bar,
                progress_args=(msg, upload_start, "Uploading"),
            )
        else:
            await client.send_document(
                chat_id=message.chat.id,
                document=file_path,
                thumb=thumb if (thumb and os.path.exists(thumb)) else None,
                caption=caption,
                file_name=new_name,
                progress=progress_bar,
                progress_args=(msg, upload_start, "Uploading"),
            )

        await msg.edit_text("🎉 **File successfully renamed & uploaded!**")

    except Exception as e:
        await msg.edit_text(f"❌ **Error:**\n`{str(e)}`")

    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    Thread(target=run_web).start()
    print("Bot Started Live on Cloud!")
    app.run()
    
