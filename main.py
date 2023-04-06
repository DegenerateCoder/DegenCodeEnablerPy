import requests
import time
from datetime import datetime
import json


def set_gql_twitch_clientid():
    global client_id
    url = "https://www.twitch.tv/"
    response = requests.get(url)
    
    index = response.text.find("clientId=\"") 
    index += len("clientId=\"")
    end_index = response.text.find("\"",index)
    
    client_id = response.text[index:end_index]
    

def is_twitch_channel_live(channel_name):
    channel_url = f"https://gql.twitch.tv/gql"
    headers = {"Cache-Control": "no-cache, no-store, must-revalidate",
               "Pragma": "no-cache",
               "Expires": "0",
               "Surrogate-Control": "no-store",
               "Vary": "*",
               "Client-Id": f"{client_id}"}

    json_request = """
            [
                {
                    "operationName": "UseLive",
                    "variables": {
                        "channelLogin": ""
                    },
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "639d5f11bfb8bf3053b424d9ef650d04c4ebb7d94711d644afb08fe9a0fad5d9"
                        }
                    }
                }
            ]
    """
    json_request = json.loads(json_request)
    json_request[0]['variables']['channelLogin'] = channel_name

    response = requests.post(channel_url, headers=headers, json=json_request)
    if response.status_code != 200:
        print(
            f"Request error: {response.status_code}:{response.reason} for channel: {channel_name}")
        raise RuntimeError(
            f"Request failed: {response.status_code} reason: {response.reason}")

    return response.json()[0]['data']['user']['stream'] != None


def get_livestream_title(channel_name):
    channel_url = f"https://gql.twitch.tv/gql"
    headers = {"Cache-Control": "no-cache, no-store, must-revalidate",
               "Pragma": "no-cache",
               "Expires": "0",
               "Surrogate-Control": "no-store",
               "Vary": "*",
               "Client-Id": f"{client_id}"}

    json_request = """
            [
                {
                    "operationName": "FilterableVideoTower_Videos",
                    "variables": {
                        "limit": 1,
                        "channelOwnerLogin": "",
                        "broadcastType": "ARCHIVE",
                        "videoSort": "TIME"
                    },
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "a937f1d22e269e39a03b509f65a7490f9fc247d7f83d6ac1421523e3b68042cb"
                        }
                    }
                }
            ]
    """
    json_request = json.loads(json_request)
    json_request[0]['variables']['channelOwnerLogin'] = channel_name

    response = requests.post(channel_url, headers=headers, json=json_request)
    if response.status_code != 200:
        print(
            f"Request error: {response.status_code}:{response.reason} for channel: {channel_name}")
        raise RuntimeError(
            f"Request failed: {response.status_code} reason: {response.reason}")

    vid_title = response.json(
    )[0]['data']['user']['videos']['edges'][0]['node']['title']
    return vid_title


def update_twitch_channel_status(channel_name):
    is_live = is_twitch_channel_live(channel_name)
    if (twitch_channels[channel_name] != is_live):
        twitch_channels[channel_name] = is_live
        if (is_live):
            title = get_livestream_title(channel_name)
            channel_url = f"https://www.twitch.tv/{channel_name}"
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

    set_gql_twitch_clientid()

    while (True):
        monitor_twitch_channels()
        time.sleep(60)

    exit(0)
