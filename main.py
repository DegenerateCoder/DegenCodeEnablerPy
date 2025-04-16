import time
from yt_mon import monitor_youtube_channels, initialize_channels_data
from twitch_mon import monitor_twitch_channels, set_gql_twitch_clientid

if __name__ == "__main__":
    print("Hello world! from DegenCodeEnabler")

    set_gql_twitch_clientid()
    initialize_channels_data()

    while (True):
        monitor_twitch_channels()
        monitor_youtube_channels()
        time.sleep(60)

    exit(0)
