from telethon import TelegramClient
import asyncio
from telethon.tl.functions.users import GetFullUserRequest

api_id = 36809303
api_hash = "0f94015aaf0817fa9997776f13e4130f"

client = TelegramClient("session_name", api_id, api_hash)


async def main():
    user_full = await client(GetFullUserRequest("PixelKalpak"))
    user = user_full.users[0]
    text = f"нет."
    msg_ids = []

    for i in range(10):
        message = await client.send_message(user, text)
        msg_ids.append(message.id)

    await asyncio.sleep(10)

    for msg_id in msg_ids:
        await client.delete_messages(user, msg_id, revoke=True)


with client:
    client.loop.run_until_complete(main())