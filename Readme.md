## Deploy TeleGuardian & stop spammers from invading your personal space !
<br>

## PREVIEW :

[![IMG-20240915-072146.jpg](https://i.postimg.cc/FR0GTb29/IMG-20240915-072146.jpg)](https://postimg.cc/tZChT6qf)

<br>


## Prerequisites :

1.  `API_ID` & `API_HASH` : Login [here](https://my.telegram.org/auth) . select API DEVELOPEMENT TOOLS & fill the details and there you go ...

   <img align = "center" src = "https://i.postimg.cc/4xr6DZRX/fghdg.png"> 
   <img align = "center" src = "https://i.postimg.cc/KYD5BVCF/Inkedwjeh-LI.jpg">

2. `MONGODB-URI` : Visit [MongoDB ATLAS](https://www.mongodb.com/cloud/atlas/register) , sign up and fill the registration .

- Create A new Free Cluster , create username & password 
- Go to Network access and add new IP Address
- Select the option Access from anywhere (0.0.0.0/0)
- Go to Database
- In Your Cluster , choose Connect
- Choose Drivers
- select python and then copy the connection string below
- add your own username & password in the string which you created while making cluster
- that's it !

3. ` TELEGRAM_SESSION_STRING ` : You can generate it from [ here ](https://replit.com/@ErichDaniken/Generate-Telegram-String-Session#main.py)

or using this

```py
pip install telethon
from telethon import TelegramClient, events

# Replace these with your own API ID, API Hash, and phone number

api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
phone_number = 'YOUR_PHONE_NUMBER'

client = TelegramClient('session_name', api_id, api_hash)

@client.on(events.NewMessage)
async def handler(event):
    sender = await event.get_sender()
    print(f'New message from {sender.username}: {event.text}')
    
    await event.reply('Hello! This is a response from my bot.')

async def main():
    await client.start(phone=phone_number)
    print("Client is running...")
    
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
```

4. ` BOT_OWNER_ID ` : Just go to Rose bot.Send any msg and reply to ur msg with /id .

5. ` MAX_UNAPPROVED_MSG ` : No of msg any Unapproved User can send to you before being blocked !

   Recommended: 3

6. `GIF_URL` : your Gif url
7. ` GIF_CAPTION ` : Write your own caption
8. ` WARNING_MSG ` : Write Warning Msg
9. ` FINAL_MSG ` : Write Final Msg here

    [![IMG-20240915-072358.jpg](https://i.postimg.cc/3w4tvQ10/IMG-20240915-072358.jpg)](https://postimg.cc/zLNCsM9q)
   
## How it Works ?
- When anyone sends you a msg , they will instantly receive the GIF and Caption
- If they Reach the one msg less than `MAX_UNAPPROVED_MSG` , they will receive warning msg
- If they send again , they will automatically get blocked and final msg will be sent
- MongoDb is used to store the data of approved or disapproved users 

## Commands !

- `!approve` : to approve the user to text you
- `!disapprove` : to disapprove user from texting you
  

## Deploy On Railway
<br>

<div id="deploy" align="center">
  
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/_5NJ1H?referralCode=LUJMFv)

</div>

<hr>

[ 🔔 Ping Me ](https://t.me/NemesisRoy) If you get any error 

