from googleapiclient.discovery import build
import googleapiclient.errors
import googleapiclient.discovery


class yt_conn(object):

    def __init__(self, API_key):

        """Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
        """

        scopes_yt = ["https://www.googleapis.com/auth/youtube"]
        api_service_name = "youtube"
        api_version = "v3"

        self.youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=API_key)

    def process_channel_id(self, channel_id):
        # get the channel details from channel id
        request = self.youtube.channels().list(
            part="brandingSettings,statistics,topicDetails,status,contentOwnerDetails,contentDetails,localizations",
            id=channel_id)
        channel_details = request.execute()

        return channel_details

    def get_videos_of_channel(self, channel_details, max_results):
        # get upload playlist_id from channel_details
        playlist_id = channel_details.get('items')[0].get('contentDetails').get('relatedPlaylists').get('uploads')

        # get the playlist details with playlist_id
        request = self.youtube.playlistItems().list(playlistId=playlist_id, part='snippet,contentDetails',
                                                    maxResults=50)
        playlist_details = request.execute()

        return playlist_details

    def get_video_details(self, id_list):
        request = self.youtube.videos().list(
            part="contentDetails,liveStreamingDetails,localizations,contentDetails,player,recordingDetails,snippet,"
                 "statistics,status,topicDetails",
            id=id_list
        )
        videos_details = request.execute()

        return videos_details

    def get_comment_thread(self, video_id):
        request = self.youtube.commentThreads().list(
            part="snippet",
            maxResults=100,
            videoId=video_id,
            textFormat="plainText"
        )
        comment_details = request.execute()

        return comment_details
