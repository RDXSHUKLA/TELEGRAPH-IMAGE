import os
import time
import string
import random
import requests
import traceback
import asyncio
import datetime
import aiofiles
import logging
from random import choice

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from telegraph import upload_file
from database import Database

# Fetch environment variables
UPDATES_CHANNEL = os.environ.get("UPDATES_CHANNEL", "")
BOT_OWNER = int(os.environ.get("BOT_OWNER", 0))  # Default to 0 if not found
DATABASE_URL = os.environ.get("DATABASE_URL", "")
db = Database(DATABASE_URL, "TGraphRoBot")

Bot = Client(
    "Telegraph Uploader Bot",
    bot_token=os.environ["BOT_TOKEN"],
    api_id=int(os.environ["API_ID"]),
    api_hash=os.environ["API_HASH"],
)

DOWNLOAD_LOCATION = "./DOWNLOADS/XFLSWAN/TELEGRAPH"

START_TEXT =  """
**┌─────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼ ───────•
┆
┆Ⰶ нᴇʏ {}
┆
┆Ⰶ ɴɪᴄᴇ ᴛᴏ ᴍᴇᴇᴛ ʏᴏᴜ ! 
┆
└─────────────────────────•
┆❖ ɪ ᴀᴍ ᴀ ᴛᴇʟᴇɢʀᴀᴘʜ ɢᴇɴᴇʀᴀᴛᴇ ʙᴏᴛ
┆❖ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴍᴇ ɢᴇɴ ᴛᴇʟᴇɢʀᴀᴘʜ ʟɪɴᴋ 
┆❖ sᴜᴘᴘᴏʀᴛ - ɢᴘɢ | ᴘɴɢ | ʙʏ-ᴄᴀᴛʙᴏx
┆❖ ʙʏ : [sᴛʀᴀɴɢᴇʀ ᴀssᴏᴄɪᴀᴛɪᴏɴ](https://t.me/StrangerAssociation) 🚩
└─────────────────────────•**"""

HELP_TEXT = """**┌─────────────────────────•
┆
┆Ⰶ ʜᴇʏ, ғᴏʟʟᴏᴡ ᴛʜᴇsᴇ sᴛᴇᴘs:-
┆
┆❖ ᴊᴜsᴛ sᴇɴᴅ ᴍᴇ ᴀ ᴍᴇᴅɪᴀ ᴜɴᴅᴇʀ 𝟻ᴍʙ.
┆
┆❖ ᴛʜᴇɴ ɪ ᴡɪʟʟ ᴅᴏᴡɴʟᴏᴀᴅ ɪᴛ.
┆
┆❖ 𝙰ғᴛᴇʀ ᴛʜᴀᴛ ɪ ᴡɪʟʟ ᴜᴘʟᴏᴀᴅᴇᴅ ᴛʜᴇ 
┆   ᴛᴇʟᴇɢʀᴀᴘʜ ʟɪɴᴋ └─────────────────────────•**"""

ABOUT_TEXT = """**┌──────˹ ᴀʙᴏᴜᴛ ᴛʜɪꜱ ʙᴏᴛ ˼───────•
┆✤ ʙᴏᴛ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴛᴇʟᴇɢʀᴀᴘʜ ʟɪɴᴋ
┆
┆❖ ʙᴏᴛ ʙʏ [sᴛʀᴀɴɢᴇʀ ᴀssᴏᴄɪᴀᴛɪᴏɴ](https://t.me/StrangerAssociation)
┆
┆❖ ʟᴀɴɢᴜᴀɢᴇ : [ᴘʏᴛʜᴏɴ](https://www.python.org)
┆
┆❖ ᴘᴏᴡᴇʀᴇᴅ ʙʏ : [sʜɪᴠᴀɴsʜ-xᴅ](https://t.me/SHIVANSH474)
┆
┆❖ ᴅᴇᴠᴇʟᴏᴘᴇʀ : [sʜɪᴠᴀɴsʜ](https://t.me/SHIVANSHDEVS)
└─────────────────────────•**"""

START_BUTTONS = InlineKeyboardMarkup(
    [[
        InlineKeyboardButton(' ▪️ ʜᴇʟᴘ  ▪️', callback_data='help'),
        InlineKeyboardButton(' ▪️  ᴀʙᴏᴜᴛ  ▪️︎', callback_data='about'),
    ],
    [
        InlineKeyboardButton(' ▪️ sᴜᴘᴘᴏʀᴛ  ▪️', url='https://t.me/MASTIWITHFRIENDSXD'),
        InlineKeyboardButton(' ▪️ ᴜᴘᴅᴀᴛᴇ  ▪️︎', url='https://t.me/SHIVANSH474'),
    ],
     [
         InlineKeyboardButton(' ▪️ ᴄʟᴏsᴇ ▪️︎', callback_data='close')
     ]]
)

HELP_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(' ▪️ ʜᴏᴍᴇ ▪️ ', callback_data='home'),
            InlineKeyboardButton(' ▪️︎︎︎ᴀʙᴏᴜᴛ ︎▪️︎︎', callback_data='about')
        ],
        [
            InlineKeyboardButton(' ▪️ ᴄʟᴏsᴇ ▪️︎', callback_data='close')
        ]
    ]
)

ABOUT_BUTTONS = InlineKeyboardMarkup(
    [[
        InlineKeyboardButton(' ▪️ ʜᴏᴍᴇ ▪️ ', callback_data='home'),
        InlineKeyboardButton(' ▪️ ʜᴇʟᴘ ▪️ ︎', callback_data='help'),
    ],
     [
         InlineKeyboardButton(' ▪️ ᴄʟᴏsᴇ  ▪️︎', callback_data='close')
     ]]
)

# Error handling
async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : user is blocked\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception as e:
        return 500, f"{user_id} : {traceback.format_exc()}\n"


# Callback Query Handling
@Bot.on_callback_query()
async def cb_handler(bot, update):
    if update.data == "home":
        await update.message.edit_text(
            text=START_TEXT.format(update.from_user.mention),
            reply_markup=START_BUTTONS,
            disable_web_page_preview=True
        )
    elif update.data == "help":
        await update.message.edit_text(
            text=HELP_TEXT,
            reply_markup=HELP_BUTTONS,
            disable_web_page_preview=True
        )
    elif update.data == "about":
        await update.message.edit_text(
            text=ABOUT_TEXT.format((await bot.get_me()).username),
            reply_markup=ABOUT_BUTTONS,
            disable_web_page_preview=True
        )
    else:
        await update.message.delete()


# Command Handlers
@Bot.on_message(filters.private & filters.command(["start"]))
async def start(bot, update):
    await update.reply_text(
        text=START_TEXT.format(update.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=START_BUTTONS
    )


@Bot.on_message(filters.private & filters.command(["help"]))
async def help(bot, update):
    await update.reply_text(
        text=HELP_TEXT,
        disable_web_page_preview=True,
        reply_markup=HELP_BUTTONS
    )


@Bot.on_message(filters.private & filters.command(["about"]))
async def about(bot, update):
    await update.reply_text(
        text=ABOUT_TEXT.format((await bot.get_me()).username),
        disable_web_page_preview=True,
        reply_markup=ABOUT_BUTTONS
    )



# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Function to upload a file to Catbox
def upload_file(file_path):
    url = "https://catbox.moe/user/api.php"
    data = {"reqtype": "fileupload", "json": "true"}

    try:
        with open(file_path, "rb") as file:
            files = {"fileToUpload": file}
            response = requests.post(url, data=data, files=files)

        logger.info(f"Response from Catbox: {response.status_code} - {response.text}")

        if response.status_code == 200:
            # Catbox returns a plain URL, not JSON
            if response.text.startswith("https://files.catbox.moe/"):
                return True, response.text.strip()
            else:
                return False, f"Unexpected response from Catbox: {response.text}"
        else:
            logger.error(f"Error from Catbox: {response.status_code} - {response.text}")
            return False, f"Error: {response.status_code} - {response.text}"

    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}")
        return False, f"Exception occurred: {str(e)}"

# Handler for incoming photo messages
@Bot.on_message(filters.photo & filters.incoming & filters.private)
async def photo_handler(_, message: Message):
    """Handles incoming photo messages by uploading to Catbox.moe."""
    media = message
    file_size = media.photo.file_size if media.photo else 0

    # Check if file is larger than 200MB
    if file_size > 200 * 1024 * 1024:
        return await message.reply_text("Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴘʜᴏᴛᴏ ᴜɴᴅᴇʀ 200MB.")

    try:
        # Initial response message
        text = await message.reply("Processing...")

        # Download the file
        local_path = await media.download()
        if not local_path or not os.path.exists(local_path):
            await text.edit_text("Failed to download the file. Please try again.")
            return

        # Inform the user that upload is in progress
        await text.edit_text("Uploading... Please wait.")

        # Upload the file to Catbox
        success, upload_url_or_error = upload_file(local_path)

        if success:
            # Prepare the message text with the upload URL
            final_text = f"[ʜᴏʟᴅ ᴛʜᴇ ʟɪɴᴋ]({upload_url_or_error})\n\n**💻 ᴘʟᴇᴀsᴇ ᴊᴏɪɴ 💗 :-** @SHIVANSH474"

            # Inline buttons with the response link
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="▪️ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ▪️", url="https://t.me/StrangerAssociation"),
                    ]
                ]
            )

            # Send final message with the URL and buttons
            await text.edit_text(
                text=final_text,
                disable_web_page_preview=True,
                reply_markup=reply_markup
            )
        else:
            # In case of failure, show the error
            await text.edit_text(f"❍ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ᴜᴘʟᴏᴀᴅɪɴɢ. {upload_url_or_error}")

    except Exception as e:
        logger.error(f"Error during file upload: {str(e)}")
        await text.edit_text("File upload failed.")

    finally:
        # Ensure that the local file is always removed
        if os.path.exists(local_path):
            os.remove(local_path)


# Broadcast Command - Allows the bot owner to broadcast a message
@Bot.on_message(filters.private & filters.command("broadcast") & filters.user(BOT_OWNER) & filters.reply)
async def broadcast(bot, update):
    broadcast_ids = {}
    all_users = await db.get_all_users()
    broadcast_msg = update.reply_to_message
    while True:
        broadcast_id = ''.join([random.choice(string.ascii_letters) for i in range(3)])
        if not broadcast_ids.get(broadcast_id):
            break
    out = await update.reply_text(text=f"ʙʀᴏᴀᴅᴄᴀsᴛ sᴛᴀʀᴛᴇᴅ! ʏᴏᴜ ᴡɪʟʟ ʙᴇ ɴᴏᴛɪғɪᴇᴅ ᴡɪᴛʜ ʟᴏɢ ғɪʟᴇ ᴡʜᴇɴ ᴀʟʟ ᴛʜᴇ ᴜsᴇʀs ᴀʀᴇ ɴᴏᴛɪғɪᴇᴅ.")
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    failed = 0
    success = 0
    broadcast_ids[broadcast_id] = dict(total=total_users, current=done, failed=failed, success=success)
    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        async for user in all_users:
            sts, msg = await send_msg(user_id=int(user['id']), message=broadcast_msg)
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await db.delete_user(user['id'])
            done += 1
            if broadcast_ids.get(broadcast_id) is None:
                break
            else:
                broadcast_ids[broadcast_id].update(dict(current=done, failed=failed, success=success))
    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await asyncio.sleep(3)
    await out.delete()
    if failed == 0:
        await update.reply_text(
            text=f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True)
    else:
        await update.reply_document(
            document='broadcast.txt',
            caption=f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed."
        )
    os.remove('broadcast.txt')


# Get bot status
@Bot.on_message(filters.private & filters.command("status"), 
group=5)
async def status(bot, update):
    total_users = await db.total_users_count()
    text = "**Bot Status**\n"
    text += f"\n**Total Users:** `{total_users}`"
    await update.reply_text(
        text=text,
        quote=True,
        disable_web_page_preview=True
    )

# Run the bot
Bot.run()