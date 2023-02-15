import requests
import datetime
import python_package
from multiprocessing import Pool
import random

def gender_summary_generator(names):
    total_count = len(names)
    male_count = 0
    female_count = 0

    for n in names:
        gender = n['gender']
        if gender == 'female':
            female_count += 1
        elif gender == 'male':
            male_count += 1

    return male_count / total_count * 100, female_count / total_count * 100


def guess_gender_parallel(names):
    with Pool(processes=4) as pool:
        results = pool.map(python_package.guess_gender_worker, names)
    return results


def average_time_between_dates(dates):
    # Convert strings to datetime objects
    dates = [datetime.fromisoformat(date) for date in dates]

    # Compute time differences in seconds
    deltas = [(dates[i+1] - dates[i]).total_seconds() for i in range(len(dates)-1)]

    # Compute average time difference in seconds
    avg_delta = sum(deltas) / len(deltas)

    # Convert to a timedelta object and then to a string in HH:MM:SS format
    avg_delta = str(datetime.utcfromtimestamp(avg_delta).time())

    return avg_delta


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


def avg(lst):
    return sum(lst) / len(lst)


def channel_data(input='https://www.youtube.com/@ImponderabiliaTV/featured'):

    if input != "":
        url = input

        print(url)

        # Get page http
        response = requests.get(url, cookies={'CONSENT': 'YES+cb.20210328-17-p0.en-GB+FX+{}'.format(random.randint(100, 999))})
        http_string = response.text

        # Get id from http
        channel_id = find_between(http_string, 'href="https://www.youtube.com/channel/', '"')

        # YT API key
        YOUTUBE_API_KEY = "AIzaSyCHjvwJ9lBTzqyp4STGEuCet489sfmJuok"

        yt_conn = python_package.yt_conn(API_key=YOUTUBE_API_KEY)

        # YT Channel API
        channel_details = yt_conn.process_channel_id(channel_id=channel_id)

        # YT Playlist API
        data_play_list = yt_conn.get_videos_of_channel(channel_details=channel_details, max_results=50)

        # Current date
        date_now = datetime.datetime.utcnow() - datetime.timedelta(days=5)
        # Get date to format yyyy-mm-ddThh-mm-ss
        date_subst = date_now.isoformat() + 'Z'

        # id list of uploaded videos
        video_id_list = data_play_list['items']

        # id list of uploaded videos limited to 5
        filtered_list = [publishDate for publishDate in video_id_list
                         if publishDate['contentDetails']['videoPublishedAt'] < date_subst][:15]

        # string to be inserted into videos API call
        video_ids = ','.join([filtered['contentDetails']['videoId'] for filtered in filtered_list])

        # Videos data
        data_videos = yt_conn.get_video_details(id_list=video_ids)

        videos_views_list = []
        videos_published_list = []
        videos_title_list = []
        videos_desc_list = []
        videos_duration_list = []
        videos_kids_list = []
        videos_like_list = []
        videos_comment_list = []
        videos_ads_list = []

        for video_id in filtered_list:
            url = f"https://www.youtube.com/watch?v={video_id['contentDetails']['videoId']}"
            response = requests.get(url)
            if "paidContentOverlayRenderer" in response.text:
                videos_ads_list.append(True)
            else:
                videos_ads_list.append(False)

        first_ad_count = videos_ads_list[0:1].count(True)
        first_five_ad_count = videos_ads_list[0:5].count(True)
        overall_ad_count = videos_ads_list.count(True)

        comments = []
        for video_id in [filtered_list[1], filtered_list[5], filtered_list[10]]:
            comments.append(yt_conn.get_comment_thread(video_id=video_id['contentDetails']['videoId']))

        comment_author = []
        for vid_comments in comments:
            for comment in vid_comments['items']:
                comment_author.append(comment['snippet']['topLevelComment']['snippet']['authorDisplayName'])

        comment_author = list(set(comment_author))

        gender_list = guess_gender_parallel(comment_author)

        gender_list_filtered = [n for n in gender_list if n['gender'] != 'unknown']
        male_percentage, female_percentage = gender_summary_generator(names=gender_list_filtered)

        for video in data_videos['items']:
            videos_views_list.append(int(video['statistics']['viewCount']))
            videos_like_list.append(int(video['statistics']['likeCount']))
            videos_comment_list.append(int(video['statistics']['commentCount']))
            videos_published_list.append(video['snippet']['publishedAt'])
            videos_title_list.append(video['snippet']['title'])
            videos_desc_list.append(video['snippet']['description'])
            videos_duration_list.append(video['contentDetails']['duration'])
            videos_kids_list.append(video['status']['madeForKids'])

        output = [channel_details['items'][0]['id'],   # Id
                  channel_details['items'][0]['brandingSettings']['channel']['title'],     # Title
                  avg(videos_views_list),   # Avg Views
                  min(videos_views_list),   # Min Views
                  max(videos_views_list),   # Max Views
                  avg(videos_like_list),    # Avg Likes
                  min(videos_like_list),    # Min Views
                  max(videos_like_list),    # Max Likes
                  avg(videos_comment_list),     # Avg Comment count
                  min(videos_comment_list),     # Min Comment count
                  max(videos_comment_list),     # Max Comment count
                  int(avg(videos_views_list))/int(channel_details['items'][0]['statistics']['subscriberCount']),
                  # Views to sub ratio
                  first_ad_count,       # Last video ad
                  first_five_ad_count,  # Five last videos ads count
                  overall_ad_count,     # Fifteen last videos ads count
                  male_percentage,      # Male percentage
                  female_percentage,    # Female percentage
                  channel_details['items'][0]['topicDetails']['topicCategories'][0],   # Categories
                  channel_details['items'][0]['brandingSettings']['channel']['country'],   # Country
                  channel_details['items'][0]['brandingSettings']['channel']['description'],   # Description
                  channel_details['items'][0]['statistics']['subscriberCount'],    # Subscriber Count
                  channel_details['items'][0]['statistics']['videoCount'],     # Video Count
                  channel_details['items'][0]['statistics']['viewCount'],      # Views Count
                  data_videos['items'][0]['snippet']['publishedAt']      # Published at
                  ]

        return output

channel_data()