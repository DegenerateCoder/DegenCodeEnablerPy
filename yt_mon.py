from typing import Any
import requests
from datetime import datetime
from dataclasses import dataclass
from bot import notify

import pickle
import os


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

piped_api_domains_index = 0
piped_api_domains = [
"https://pipedapi.adminforge.de",
"https://api.piped.yt"
]

piped_instance = "https://piped.yt"


def get_piped_api_instance() -> str:
    return piped_api_domains[piped_api_domains_index]

def next_piped_api_domains_index():
    global piped_api_domains_index 
    piped_api_domains_index += 1
    if piped_api_domains_index == len(piped_api_domains): 
        piped_api_domains_index = 0 


def monitor_youtube_channels():
    print("-------")
    print(f"Updating YouTube {datetime.now()}")
    for channel in youtube_channels:
        try:
            update_youtube_channel_status(channel)
            save_channels_data()
        except Exception as e:
            next_piped_api_domains_index()
            print(f"Error: {e}; for channel: {channel.name}")

    print("-------")


@dataclass
class VideoData:
    title: str
    url: str
    upload_timestamp: int
    channel_json: Any 


# TODO: can fail
def get_latest_vid_details(channel_id: str) -> VideoData:
    piped_api_instance = get_piped_api_instance()
    channel_url = f"{piped_api_instance}/channel/{channel_id}"
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
    return VideoData(vid_title,vid_url,vid_timestamp, channel_json)


def notify_new_videos(channel_json: Any, current_url: str, current_upload_timestamp: int, channel_name: str):
    related_streams = channel_json['relatedStreams']
    for related_stream in related_streams:
        vid_title: str = related_stream['title']
        vid_url: str = related_stream['url']
        vid_timestamp = related_streams[0]['uploaded']
        if (current_url != vid_url and current_upload_timestamp < vid_timestamp):
            message = f"{channel_name} published new video \"{vid_title}\"; \n https://www.youtube.com{vid_url} ; {piped_instance}{vid_url}"
            notify(message)
        else:
            break


def update_youtube_channel_status(channel: YTChannel):
    latest_vid_details = get_latest_vid_details(channel.id)
    vid_url = latest_vid_details.url
    vid_timestamp = latest_vid_details.upload_timestamp
    if (channel.latest_vid_url != vid_url and channel.latest_upload_timestamp < vid_timestamp):
        notify_new_videos(latest_vid_details.channel_json, channel.latest_vid_url, channel.latest_upload_timestamp, channel.name)
        channel.latest_upload_timestamp = vid_timestamp
        channel.latest_vid_url = vid_url


# TODO: can fail
def get_channel_id(channel_handle: str) -> str:
    piped_api_instance = get_piped_api_instance()
    channel_url = f"{piped_api_instance}/c/@{channel_handle}"
    response = requests.get(channel_url)
    channel_id = response.json()['id']
    return channel_id


# TODO: can fail
def get_channel_name(channel_id: str) -> str:
    piped_api_instance = get_piped_api_instance()
    channel_url = f"{piped_api_instance}/channel/{channel_id}"
    response = requests.get(channel_url)
    channel_name = response.json()["name"]
    return channel_name


# TODO: can fail
# TODO: fix unnecessary tripling of request
def initialize_channels_data():
    if channel_data_file_exists():
        load_channels_data()
    else:
        for channel in youtube_channels:
            if channel.handle != "":
                channel.id = get_channel_id(channel.handle)
            channel.name = get_channel_name(channel.id)
            latest_vid_details = get_latest_vid_details(channel.id)
            channel.latest_upload_timestamp = latest_vid_details.upload_timestamp
            channel.latest_vid_url = latest_vid_details.url
        save_channels_data()

def save_channels_data():
    with open('youtube_channels.pkl', 'wb') as f:
        pickle.dump(youtube_channels, f)

def load_channels_data():
    global youtube_channels
    with open('youtube_channels.pkl', 'rb') as f:
        youtube_channels = pickle.load(f)
    

def channel_data_file_exists() -> bool:
    file_path = 'youtube_channels.pkl'
    if os.path.isfile(file_path):
        with open('youtube_channels.pkl', 'rb') as f:
            youtube_channels_pkl = pickle.load(f)
            if len(youtube_channels_pkl) == len(youtube_channels):
                return True
        return False
    else:
        return False

