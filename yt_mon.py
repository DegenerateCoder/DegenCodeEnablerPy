import requests
from datetime import datetime
from dataclasses import dataclass


@dataclass
class YTChannel:
    handle: str
    id: str
    name: str = ""
    latest_vid_url: str = ""
    latest_upload_timestamp: int = 0

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


@dataclass
class VideoData:
    title: str
    url: str
    upload_timestamp: int


# TODO: can fail
def get_latest_vid_details(channel_id: str) -> VideoData:
    channel_url = f"https://piped-api.garudalinux.org/channel/{channel_id}"
    headers = {"Cache-Control": "no-cache, no-store, must-revalidate",
               "Pragma": "no-cache",
               "Expires": "0",
               "Surrogate-Control": "no-store",
               "Vary": "*"}
    response = requests.get(channel_url, headers=headers)

    if response.status_code != 200:
        print(
            f"Request error: {response.status_code}:{response.reason} for channel: {channel_id}")
        raise RuntimeError(
            f"Request failed: {response.status_code} reason: {response.reason}")

    channel_json = response.json()
    related_streams = channel_json['relatedStreams']
    vid_title = related_streams[0]['title']
    vid_url = related_streams[0]['url']
    vid_timestamp = related_streams[0]['uploaded']
    return VideoData(vid_title,vid_url,vid_timestamp)


def update_youtube_channel_status(channel: YTChannel):
    latest_vid_details = get_latest_vid_details(channel.id)
    vid_title = latest_vid_details.title
    vid_url = latest_vid_details.url
    vid_timestamp = latest_vid_details.upload_timestamp
    if (channel.latest_vid_url != vid_url and channel.latest_upload_timestamp < vid_timestamp):
        message = f"{channel.name} published new video \"{vid_title}\"; \n https://piped.garudalinux.org{vid_url}"
        notify(message)
        channel.latest_upload_timestamp = vid_timestamp
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
        latest_vid_details = get_latest_vid_details(channel.id)
        channel.latest_upload_timestamp = latest_vid_details.upload_timestamp
        channel.latest_vid_url = latest_vid_details.url


def notify(notification_message: str):
    # TODO
    print(notification_message)
