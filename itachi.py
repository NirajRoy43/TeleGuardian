import logging
from telethon import TelegramClient, events
from telethon.tl.functions.contacts import BlockRequest
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
from pymongo import MongoClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Your Telegram API credentials
api_id = '4484756'
api_hash = 'd90223b0899a3bd493d63d93823ae6c8'

client = TelegramClient('session_name', api_id, api_hash)

# MongoDB Atlas connection
mongo_client = MongoClient('mongodb+srv://Okayniraj:Okayniraj143@cluster0.t95k4et.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = mongo_client['test']  # Replace 'test' with your actual database name
approved_users_collection = db['approved_users']

# Spam protection settings
MAX_UNAPPROVED_MESSAGES = 5
user_message_count = {}
approved_users = set()  # Set to store approved users

# Path to the GIF file
video_or_gif_path = 'https://i.postimg.cc/fWgdYxf8/21970003.gif'  # Change this to your actual file path

@client.on(events.NewMessage(incoming=True))
async def handle_pm(event):
    chat_id = event.chat_id
    sender = await event.get_sender()

    # Ignore messages from groups or channels
    if event.is_group or event.is_channel:
        return

    # If the user is approved, allow the messages
    if sender.id in approved_users:
        return

    # Track the user's messages
    if sender.id not in user_message_count:
        user_message_count[sender.id] = 1

        # Send a professional-looking message with video/GIF
        await client.send_file(
            sender.id,
            video_or_gif_path,
            caption=("👋 **Konnichiwa , Shiranai hito!**\n\n"
			"Watashi wa **ITACHI UCHIHA** desu, the digital guardian of my Boss's Realm. 🥷⛩️\n\n"
			"Your message is in the queue, so don't rush.\n"
			"Don't spam , else you'll be hit with Amaterasu!🌀⚡\n\n"
			"~ SAYONARA 🍂"
            )
        )
    else:
        # Increment the message count for the user
        user_message_count[sender.id] += 1

        # Warn the user if they are close to the limit
        if user_message_count[sender.id] == MAX_UNAPPROVED_MESSAGES - 1:
            await event.reply(
                f"Huh, You DUMB!😒\n"
                f"Send one more messages & you'll be under my Genjutsu!🤧"
            )

    # Check if the user has sent more than the allowed number of messages
    if user_message_count[sender.id] >= MAX_UNAPPROVED_MESSAGES:
        # Block the user
        await client(BlockRequest(id=sender.id))

        # Send a final notice before blocking
        await client.send_message(
            sender.id,
            "Doke,Bakayarou 🤡"
            
        )

        # Optionally, delete the user's messages (if desired)
        # await client.delete_messages(chat_id, [event.message.id for _ in range(user_message_count[sender.id])])

@client.on(events.NewMessage(pattern='!approve'))
async def approve_user(event):
    if event.is_reply:
        reply_message = await event.get_reply_message()
        sender = await reply_message.get_sender()
        # Add user to approved list
        approved_users.add(sender.id)
        approved_users_collection.update_one(
            {'user_id': sender.id},
            {'$set': {'user_id': sender.id, 'username': sender.username}},
            upsert=True
        )
        await event.respond(f"User {sender.username} approved to message you.")
    else:
        await event.respond("Reply to a user's message with !approve to approve them.")

@client.on(events.NewMessage(pattern='!disapprove'))
async def disapprove_user(event):
    if event.is_reply:
        reply_message = await event.get_reply_message()
        sender = await reply_message.get_sender()
        # Remove user from approved list
        approved_users.discard(sender.id)
        approved_users_collection.delete_one({'user_id': sender.id})
        await event.respond(f"User {sender.username} disapproved from messaging you.")
    else:
        await event.respond("Reply to a user's message with !disapprove to disapprove them.")

# Start the Telegram client
client.start()
client.run_until_disconnected()