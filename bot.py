import asyncio
from nio import AsyncClient


async def send_message(message: str):
    client = AsyncClient("https://matrix-client.matrix.org",
                         "", device_id="")

    await client.login("", device_name="bot")
    await client.room_send(
        room_id="",
        message_type="m.room.message",
        content={
            "msgtype": "m.text",
            "body": message
        }
    )
    await client.close()


def notify(notification_message: str):
    # TODO
    print(f"{notification_message}\n")
    asyncio.get_event_loop().run_until_complete(send_message(notification_message))
