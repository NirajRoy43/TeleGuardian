import os
import logging
import asyncio
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.contacts import BlockRequest
from pymongo import MongoClient
from telethon.sessions import StringSession

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Your credentials for environment variables
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_owner_id = os.getenv('BOT_OWNER_ID')
session_string = os.getenv('TELEGRAM_SESSION_STRING')
video_or_gif_path = os.getenv('GIF_URL')
mongo_uri = os.getenv('MONGODB_URI')

# Initialize the Telegram client with the bot token
client = TelegramClient(StringSession(session_string), api_id, api_hash)

# MongoDB Atlas 

mongo_client = MongoClient(mongo_uri)
db = mongo_client['test']  
approved_users_collection = db['approved_users']

# Spam protection settings
MAX_UNAPPROVED_MESSAGES = int(os.getenv('MAX_UNAPPROVED_MSG'))
user_message_count = {}
approved_users = set()  

async def main():
    # Start the client with the session string
    await client.start()

    # Load approved users from MongoDB at startup (synchronous iteration)
    for user in approved_users_collection.find():
        approved_users.add(user['user_id'])
        logger.info(f"Loaded approved user: {user['username']} (ID: {user['user_id']})")

    logger.info("Approved users loaded from MongoDB.")

# Dictionary to keep track of messages sent by the bot (store message IDs per user)
bot_messages = {}

@client.on(events.NewMessage(incoming=True))
async def handle_pm(event):
    chat_id = event.chat_id
    sender = await event.get_sender()

    # Ignore messages from groups or channels or bots
    if event.is_group or event.is_channel or sender.bot :
        return

    # If the user is approved, allow the messages
    if sender.id in approved_users:
        return

    # Check if the user is disapproved
    if sender.id not in approved_users:
        # Track the user's messages
        if sender.id not in user_message_count:
            user_message_count[sender.id] = 1

            # Send a professional-looking message with video/GIF and store the message ID
            gif_message = await client.send_file(
                sender.id,
                video_or_gif_path,
                caption=os.getenv('GIF_CAPTION')
            )

            # Store the message ID in the bot_messages dictionary
            bot_messages[sender.id] = [gif_message.id]

        else:
            # Increment the message count for the user
            user_message_count[sender.id] += 1

            # Warn the user if they are close to the limit
            if user_message_count[sender.id] == MAX_UNAPPROVED_MESSAGES - 1:
                warning_message = await event.reply(os.getenv('WARNING_MESSAGE'))

                # Initialize the bot_messages entry if it doesn't exist
                if sender.id not in bot_messages:
                    bot_messages[sender.id] = []  # Create an empty list for this user

                # Store the warning message ID in the bot_messages dictionary
                bot_messages[sender.id].append(warning_message.id)

        # Check if the user has sent more than the allowed number of messages
        if user_message_count[sender.id] >= MAX_UNAPPROVED_MESSAGES:
            # Block the user
            await client(BlockRequest(id=sender.id))

            # Send a final notice before blocking and store the message ID
            final_message = await client.send_message(
                sender.id,
                os.getenv('FINAL_MESSSAGE')
            )
            # Ensure the bot_messages entry exists
            if sender.id not in bot_messages:
                bot_messages[sender.id] = []

            bot_messages[sender.id].append(final_message.id)
            

@client.on(events.NewMessage(pattern='!approve'))
async def approve_user(event):
    sender = await event.get_sender()

    # Only the bot owner can approve users
    if sender.id == int(bot_owner_id):
        if event.is_reply:
            reply_message = await event.get_reply_message()
            user_to_approve = await reply_message.get_sender()

            # Add the user to the approved list
            approved_users.add(user_to_approve.id)
            approved_users_collection.update_one(
                {'user_id': user_to_approve.id},
                {'$set': {'user_id': user_to_approve.id, 'username': user_to_approve.username}},
                upsert=True
            )

            # Send an approval message
            approval_message = await event.respond(f"User {user_to_approve.username} approved to message you.")

            # Edit the approval message to notify the user
            await approval_message.edit(f"User {user_to_approve.username} has been approved to message you.")
            await asyncio.sleep(2)  # Optional: Wait for a moment before deleting

            # Delete the approval message
            await approval_message.delete()

            # Delete the bot's previous messages for this user (GIF, warnings, etc.)
            if user_to_approve.id in bot_messages:
                for message_id in bot_messages[user_to_approve.id]:
                    try:
                        await client.delete_messages(user_to_approve.id, message_id)
                    except Exception as e:
                        logger.error(f"Failed to delete message {message_id}: {e}")

                # Clear the stored messages after deleting them
                del bot_messages[user_to_approve.id]
        else:
            await event.respond("Reply to a user's message with !approve to approve them.")
    else:
        await event.respond("You don't have permission to use this command.")

@client.on(events.NewMessage(pattern='!disapprove'))
async def disapprove_user(event):
    sender = await event.get_sender()

    # Only the bot owner can disapprove users
    if sender.id == int(bot_owner_id):
        if event.is_reply:
            reply_message = await event.get_reply_message()
            user_to_disapprove = await reply_message.get_sender()

            # Remove user from approved list
            approved_users.discard(user_to_disapprove.id)
            approved_users_collection.delete_one({'user_id': user_to_disapprove.id})

            # Send a disapproval message
            disapproval_message = await event.respond(f"User {user_to_disapprove.username} disapproved from messaging you.")

            # Edit the disapproval message to notify the user
            await disapproval_message.edit(f"User {user_to_disapprove.username} has been disapproved from messaging you.")
            await asyncio.sleep(2)  # Optional: Wait for a moment before deleting

            # Delete the disapproval message
            await disapproval_message.delete()

            user_message_count[user_to_disapprove.id] = 0

            # Send a new message to notify about the disapproval
            notification_message = await client.send_message(
                user_to_disapprove.id,
                "You have been disapproved. No further messages will be processed."
            )
            bot_messages[user_to_disapprove.id] = [notification_message.id]

            # Delete the bot's previous messages for this user (GIF, warnings, etc.)
            if user_to_disapprove.id in bot_messages:
                for message_id in bot_messages[user_to_disapprove.id]:
                    try:
                        await client.delete_messages(user_to_disapprove.id, message_id)
                    except Exception as e:
                        logger.error(f"Failed to delete message {message_id}: {e}")

                # Clear the stored messages after deleting them
                del bot_messages[user_to_disapprove.id]
        else:
            await event.respond("Reply to a user's message with !disapprove to disapprove them.")
    else:
        await event.respond("You don't have permission to use this command.")

# Start the Telegram client
with client:
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
