import os
import time
import asyncio
from pyrogram import Client, filters
loop = asyncio.get_event_loop_policy().get_event_loop()
asyncio.set_event_loop(loop)

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

# Live Speed & Progress Bar
async def progress_bar(current, total, status_message, start_time, action):
    now = time.time()
    diff = now - start_time
    if round(diff % 3) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff if diff > 0 else 0
        
        current_mb = round(current / (1024 * 1024), 1)
        total_mb = round(total / (1024 * 1024), 1)
        speed_mb = round(speed / (1024 * 1024), 2)

        progress_text = (
            f"⚡ **{action}...**\n\n"
            f"📊 **Progress:** `{percentage:.1f}%`\n"
            f"📁 **Downloaded:** `{current_mb} MB / {total_mb} MB`\n"
            f"🚀 **Speed:** `{speed_mb} MB/s`"
        )
        try:
            await status_message.edit_text(progress_text)
        except Exception:
            pass

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text(
        "🔥 **Brad Pitt File Renamer Bot Ready!**\n\n"
        "1. Send Channel Logo Photo for Thumbnail.\n"
        "2. Forward Movie file to rename!"
    )

@app.on_message(filters.photo & filters.private)
async def save_photo(client, message):
    user_id = message.from_user.id
    path = f"thumb_{user_id}.jpg"
    await message.download(file_name=path)
    user_thumbs[user_id] = path
    await message.reply_text("✅ Unga **Thumbnail** Save aaidichi!")

@app.on_message(filters.private & (filters.document | filters.video))
async def process_file(client, message):
    user_id = message.from_user.id
    msg = await message.reply_text("⏳ **Connecting to Cloud Server...**")

    if message.document:
        old_name = message.document.file_name or "Movie.mkv"
    elif message.video:
        old_name = message.video.file_name or "Movie.mp4"
    else:
        old_name = "Movie.mkv"

    new_name = f"[Brad Pitt] {old_name}"
    file_path = os.path.join(os.getcwd(), new_name)
    start_time = time.time()

    try:
        # Fast Cloud Download
        downloaded_file = await message.download(
            file_name=file_path,
            progress=progress_bar,
            progress_args=(msg, start_time, "📥 Downloading File")
        )

        thumb = user_thumbs.get(user_id, None)
        caption = f"🎬 **{new_name}**\n\n❤️ **Join:** {CHANNEL_TAG}"
        upload_start_time = time.time()

        # Fast Cloud Upload
        if message.video:
            await client.send_video(
                chat_id=message.chat.id,
                video=downloaded_file,
                thumb=thumb if (thumb and os.path.exists(thumb)) else None,
                caption=caption,
                file_name=new_name,
                progress=progress_bar,
                progress_args=(msg, upload_start_time, "📤 Uploading File")
            )
        else:
            await client.send_document(
                chat_id=message.chat.id,
                document=downloaded_file,
                thumb=thumb if (thumb and os.path.exists(thumb)) else None,
                caption=caption,
                file_name=new_name,
                progress=progress_bar,
                progress_args=(msg, upload_start_time, "📤 Uploading File")
            )

        await msg.edit_text("🎉 **File successfully renamed & uploaded!**")

    except Exception as e:
        await msg.edit_text(f"❌ **Error:**\n`{e}`")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

print("Bot Started Live on Cloud!")
app.run()
