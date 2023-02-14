import requests
import datetime


def avg(lst):
    return sum(lst) / len(lst)


def channel_data(input='https://www.youtube.com/c/BudnikiPokrzywi%C5%84ski'):

    if input != "":
        url = input

        # Get page http
        response = requests.get(url)
        http_string = response.content.decode('utf-8')

        # Get id from http
        channel_id = http_string[http_string.index('itemprop="channelId"') + 30:
                                 http_string.index('><span itemprop="author"') - 1]

        # YT API key
        YOUTUBE_API_KEY = "your_api_key_here"

        # YT Channel API
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=brandingSettings%2Cstatistics%2C" \
              f"topicDetails%2Cstatus%2CcontentOwnerDetails%2CcontentDetails%2Clocalizations&id=" \
              f"{channel_id}&key={YOUTUBE_API_KEY}&alt=json"
        response = requests.get(url)
        data_channel = response.json()

        # YT Playlist API
        url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?playlistId=" \
              f"{data_channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']}" \
              f"&part=snippet%2CcontentDetails&maxResults=50&key={YOUTUBE_API_KEY}&alt=json"
        response = requests.get(url)
        data_play_list = response.json()

        # Current date
        date_now = datetime.datetime.utcnow() - datetime.timedelta(days=5)
        # Get date to format yyyy-mm-ddThh-mm-ss
        date_subst = date_now.isoformat() + 'Z'

        # id list of uploaded videos
        video_id_list = data_play_list['items']
        video_id_ads = []
        ad_channel_id = ''
        rnd_int = ''
        opt = {}

        # id list of uploaded videos limited to 5
        filtered_list = [publishDate for publishDate in video_id_list
                        if publishDate['contentDetails']['videoPublishedAt'] < date_subst][:5]

        # string to be inserted into videos API call
        video_ids = ','.join([filtered['contentDetails']['videoId'] for filtered in filtered_list])

        # YT Videos API
        url = f"https://youtube.googleapis.com/youtube/v3/videos?part=" \
              f"contentDetails%2CliveStreamingDetails%2Clocalizations%2CcontentDetails%2Cplayer%2CrecordingDetails%2C" \
              f"snippet%2Cstatistics%2Cstatus%2CtopicDetails&id={video_ids}&key={YOUTUBE_API_KEY}&alt=json"
        response = requests.get(url)
        data_videos_raw = response.json()
        data_videos = data_videos_raw['items']

        videos_views_list = []
        videos_published_list = []
        videos_title_list = []
        videos_desc_list = []
        videos_duration_list = []
        videos_kids_list = []
        videos_like_list = []
        videos_comment_list = []

        for video in data_videos:
            videos_views_list.append(int(video['statistics']['viewCount']))
            videos_like_list.append(int(video['statistics']['likeCount']))
            videos_comment_list.append(int(video['statistics']['commentCount']))
            videos_published_list.append(video['snippet']['publishedAt'])
            videos_title_list.append(video['snippet']['title'])
            videos_desc_list.append(video['snippet']['description'])
            videos_duration_list.append(video['contentDetails']['duration'])
            videos_kids_list.append(video['status']['madeForKids'])

        output = [data_channel['items'][0]['id'],
                  data_channel['items'][0]['brandingSettings']['channel']['title'],
                  avg(videos_views_list),
                  min(videos_views_list),
                  max(videos_views_list),
                  avg(videos_like_list),
                  min(videos_like_list),
                  max(videos_like_list),
                  avg(videos_comment_list),
                  min(videos_comment_list),
                  max(videos_comment_list),
                  data_channel['items'][0]['topicDetails']['topicCategories'][0],
                  data_channel['items'][0]['brandingSettings']['channel']['country'],
                  data_channel['items'][0]['brandingSettings']['channel']['description'],
                  data_channel['items'][0]['brandingSettings']['channel']['keywords'],
                  data_channel['items'][0]['statistics']['subscriberCount'],
                  data_channel['items'][0]['statistics']['videoCount'],
                  data_channel['items'][0]['statistics']['viewCount'],
                  data_videos[0]['snippet']['publishedAt']
                  ]

        return output
