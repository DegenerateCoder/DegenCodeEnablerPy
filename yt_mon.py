import requests
from datetime import datetime
from dataclasses import dataclass


@dataclass
class YTChannel:
    handle: str
    id: str
    name: str = ""
    latest_vid_url: str = ""


youtube_channels = [
    YTChannel("channel1", ""),
    YTChannel("", "channel2_id")
]


def monitor_youtube_channels():
    print("-------")
    print(f"Updating YouTube {datetime.now()}")
    for channel in youtube_channels:
        try:
            update_youtube_channel_status(channel)
        except Exception as e:
            print(f"Error: {e}; for channel: {channel.name}")

    print("-------")


# TODO: can fail
def get_latest_vid_title_and_url(channel_id: str) -> tuple[str, str]:
    channel_url = f"https://piped-api.garudalinux.org/channel/{channel_id}"
    response = requests.get(channel_url)

    if response.status_code != 200:
        print(
            f"Request error: {response.status_code}:{response.reason} for channel: {channel_id}")
        raise RuntimeError(
            f"Request failed: {response.status_code} reason: {response.reason}")

    channel_json = response.json()
    related_streams = channel_json['relatedStreams']
    vid_title = related_streams[0]['title']
    vid_url = related_streams[0]['url']
    return (vid_title, vid_url)


def update_youtube_channel_status(channel: YTChannel):
    latest_vid_details = get_latest_vid_title_and_url(channel.id)
    vid_title = latest_vid_details[0]
    vid_url = latest_vid_details[1]
    if (channel.latest_vid_url != vid_url):
        message = f"{channel.name} published new video \"{vid_title}\"; \n https://piped.garudalinux.org{vid_url}"
        notify(message)
        channel.latest_vid_url = vid_url


# TODO: can fail
def get_channel_id(channel_handle: str) -> str:
    channel_url = f"https://piped-api.garudalinux.org/c/@{channel_handle}"
    response = requests.get(channel_url)
    channel_id = response.json()['id']
    return channel_id


# TODO: can fail
def get_channel_name(channel_id: str) -> str:
    channel_url = f"https://piped-api.garudalinux.org/channel/{channel_id}"
    response = requests.get(channel_url)
    channel_name = response.json()["name"]
    return channel_name


# TODO: can fail
# TODO: fix unnecessary tripling of request
def initialize_channels_data():
    for channel in youtube_channels:
        if channel.handle != "":
            channel.id = get_channel_id(channel.handle)
        channel.name = get_channel_name(channel.id)
        latest_vid_details = get_latest_vid_title_and_url(channel.id)
        channel.latest_vid_url = latest_vid_details[1]


def notify(notification_message: str):
    # TODO
    print(notification_message)
