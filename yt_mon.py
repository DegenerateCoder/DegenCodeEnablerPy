import requests
import time
from datetime import datetime
import sys


youtube_channels = {
    "channel1": "",
    "channel2": "",
}


def monitor_youtube_channels():
    print("-------")
    print(f"Updating YouTube {datetime.now()}")
    for channel_name in youtube_channels:
        try:
            update_youtube_channel_status(channel_name)
        except Exception as e:
            print(f"Error: {e}; for channel: {channel_name}")

    print("-------")


def extract_latest_vid_title_and_url(channel_response):
    channel_json = channel_response.json()
    related_streams = channel_json['relatedStreams']
    vid_title = related_streams[0]['title']
    vid_url = related_streams[0]['url']
    return (vid_title, vid_url)


def update_youtube_channel_status(channel_name):
    channel_url = f"https://piped-api.garudalinux.org/c/@{channel_name}"
    response = requests.get(channel_url)

    if response.status_code != 200:
        print(
            f"Request error: {response.status_code}:{response.reason} for channel: {channel_name}")
        raise RuntimeError(
            f"Request failed: {response.status_code} reason: {response.reason}")

    latest_vid_details = extract_latest_vid_title_and_url(response)
    vid_title = latest_vid_details[0]
    vid_url = latest_vid_details[1]
    if (youtube_channels[channel_name] != vid_title):
        if (youtube_channels[channel_name] != ""):
            message = f"{channel_name} published new video \"{vid_title}\"; \n https://piped.garudalinux.org{vid_url}"
            notify(message)
        youtube_channels[channel_name] = vid_title


def notify(notification_message):
    # TODO
    print(notification_message)
