import requests
import time
from datetime import datetime
from yt_mon import monitor_youtube_channels

def is_twitch_channel_live(channel_response):
    live_identifiers = ["<script type=\"application/ld+json\">",
                        "https://static-cdn.jtvnw.net/previews-ttv/live_user_"]
    matched_id_count = 0
    for identifier in live_identifiers:
        if identifier in channel_response.text:
            matched_id_count += 1

    return matched_id_count == len(live_identifiers)


def extract_livestream_title(channel_response):
    description_tag = "<meta property=\"og:description\" content=\""

    des_start_index = channel_response.text.find(description_tag)
    des_end_index = 0
    if (des_start_index != -1):
        des_start_index += len(description_tag)
        des_end_index = channel_response.text.find("\"", des_start_index)
    else:  # different order of attributes
        description_tag = "\" property=\"og:description\"/>"
        des_end_index = channel_response.text.find(description_tag)
        des_start_index = channel_response.text.rfind("\"", 0, des_end_index)
        des_start_index += 1

    livestream_title = channel_response.text[des_start_index:des_end_index]
    return livestream_title


def update_twitch_channel_status(channel_name):
    channel_url = f"https://www.twitch.tv/{channel_name}"
    headers = {"Cache-Control": "no-cache, no-store, must-revalidate",
               "Pragma": "no-cache",
               "Expires": "0",
               "Surrogate-Control": "no-store",
               "Vary": "*"}
    response = requests.get(channel_url, headers=headers)
    # sometimes twitch returns generic html response instead of channel one
    while not (channel_name in response.text):
        response = requests.get(channel_url, headers=headers)

    if response.status_code != 200:
        print(
            f"Request error: {response.status_code}:{response.reason} for channel: {channel_name}")
        raise RuntimeError(
            f"Request failed: {response.status_code} reason: {response.reason}")

    is_live = is_twitch_channel_live(response)
    if (twitch_channels[channel_name] != is_live):
        twitch_channels[channel_name] = is_live
        if (is_live):
            title = extract_livestream_title(response)
            message = f"{channel_name} is Live! {title} \n{channel_url}"
            notify(message)
        else:
            message = f"{channel_name} has gone offline"
            notify(message)


def monitor_twitch_channels():
    print("-------")
    print(f"Updating Twitch {datetime.now()}")
    for channel_name in twitch_channels:
        try:
            update_twitch_channel_status(channel_name)
        except Exception as e:
            print(f"Error: {e}; for channel: {channel_name}")

    print("-------")


def notify(notification_message):
    # TODO
    print(notification_message)


if __name__ == "__main__":
    print("Hello world! from DegenCodeEnabler")

    global twitch_channels
    twitch_channels = {
        "channel1": False,
        "channel2": False
    }

    while (True):
        monitor_twitch_channels()
        monitor_youtube_channels()
        time.sleep(60)

    exit(0)
