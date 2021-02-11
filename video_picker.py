from googleapiclient.discovery import build
from datetime import datetime, timedelta, date
import pandas as pd
import yaml

# Set dataframe max row display
pd.set_option('display.max_row', 10)

# Set dataframe max column width to 20
pd.set_option('display.max_columns', 20)

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
TODAY_DATE = date.today()

def get_start_date_string(search_period_days):
    """Returns string for date at start of search period."""
    search_start_date = datetime.today() - timedelta(search_period_days)
    date_string = datetime(year=search_start_date.year, month=search_start_date.month, day=search_start_date.day).strftime('%Y-%m-%dT%H:%M:%SZ')
    return date_string

def search_each_term(search_term, api_key, uploaded_since, views_threshold=5000):
    """Uses search term to execute API calls and print results."""
    # if type(search_term) == str:
    df = generate_df(views_threshold, search_term, api_key, uploaded_since)
    df = df.sort_values(['Score'], ascending=[0])
    df = df[["Title","Channel Name","Subscribers","Views","Video URL"]]
    df.to_csv(f"{TODAY_DATE}.csv", index=False)
    return df

def search_youtube_api(search_term, api_key, uploaded_since):
    """
    Executes search through API and returns result
    q: string, Specifies the query term to search for
    part: string, Specifies a comma-separated list of one or more search resource properties that the API response will include. Value is snippet (required)
    type: string, Restricts a search query to only retrieve a particular type of resource. The value is a comma-separated list of resource types.
    order: string, Specifies the method that will be used to order resources in the API response.
        date - Sorted in reverse chronological order based on the date they were created.
        rating - Sorted from highest to lowest rating.
        relevance - Sorted based on their relevance to the search query. This is the default value for this parameter.
        title - Sorted alphabetically by title.
        videoCount - Sorted in descending order of their number of uploaded videos.
        viewCount - Sorted from highest to lowest number of views.
    maxResults: integer, Specifies the max number of items that should be returned in the result set
    publishedAfter: string, Indicates that the API response should only contain resources created after the specified time. (1970-01-01T00:00:00Z).
    """
    # Initialise API Call
    youtube_api = build(serviceName=YOUTUBE_API_SERVICE_NAME, version=YOUTUBE_API_VERSION, developerKey=api_key, cache_discovery=False)      # googleapiclient.discovery.Resource object
    
    # API Search Response
    search_result = youtube_api.search().list(
        q=search_term,
        part='snippet',
        type='video',
        order='viewCount',
        maxResults=10,
        publishedAfter=uploaded_since
    ).execute()
    return search_result,youtube_api

def how_old(item):
    """
    Extracts date string from the search item, the time when the video was published
    Converts date string to datetime object
    Finds the number of days after the video was published
    """
    when_published = item['snippet']['publishedAt']
    when_published_datetime_object = datetime.strptime(when_published,'%Y-%m-%dT%H:%M:%SZ')
    today_date = datetime.today()                                               
    days_since_published = int((today_date - when_published_datetime_object).days)
    if days_since_published == 0:
        days_since_published = 1
    return days_since_published

def view_to_sub_ratio(viewcount, num_subscribers):
    """
    Sets a logical ratio between the viewcount and the number of subscribers to make sure videos are valued on a fair base.
    We eliminate the advantages of big channels and small channels over each other
    """
    if num_subscribers == 0:
        return 0
    else:
        ratio = viewcount / num_subscribers
        return ratio

def custom_score(viewcount, ratio, days_since_published):
    """
    Sets min ratio to 5 to eliminate edge cases.
    Sets a score for a video with an equation using viewcount, ratio, days_since_published
    """
    ratio = min(ratio, 5)
    score = (viewcount * ratio) / days_since_published
    return score

def find_title(item):
    """Title of the video"""
    title = item['snippet']['title']
    return title

def find_video_url(item):
    """URL of the video"""
    video_id = item['id']['videoId']
    video_url = "https://www.youtube.com/watch?v=" + video_id
    return video_url

def find_viewcount(item, youtube_api):
    """Number of views for the video"""
    video_id = item['id']['videoId']
    video_statistics = youtube_api.videos().list(id=video_id, part='statistics').execute()  # part: string, set to "statistics" that YouTube calculates for a video
    viewcount = int(video_statistics['items'][0]['statistics']['viewCount'])
    return viewcount

def find_channel_id(item):
    """Channel Id for the channel that published the video"""
    channel_id = item['snippet']['channelId']
    return channel_id

def find_channel_url(item):
    """Channel Url for the channel that published the video"""
    channel_id = item['snippet']['channelId']
    channel_url = "https://www.youtube.com/channel/" + channel_id
    return channel_url

def find_channel_title(item):
    """Channel Title of the channel that published the video"""
    channel_name = item['snippet']['channelTitle']
    return channel_name

def find_num_subscribers(item, channel_id, youtube_api):
    """Number of Subscribers of the channel that published the video"""
    subs_search = youtube_api.channels().list(id=channel_id,part='statistics').execute()
    if subs_search['items'][0]['statistics']['hiddenSubscriberCount']:
        num_subscribers = 1000000
    else:
        num_subscribers = int(subs_search['items'][0]['statistics']['subscriberCount'])
    return num_subscribers

def generate_df(views_threshold, search_term, api_key, uploaded_since):
    """Extracts relevant information and puts into dataframe"""
    # Loop over search results and add key information to dataframe
    search_result,youtube_api = search_youtube_api(search_term, api_key, uploaded_since)
    df = pd.DataFrame(columns=('Title', 'Video URL','Score','Views','Channel Name','Subscribers','Ratio','Channel URL'))
    i = 1
    for item in search_result['items']:
        viewcount = find_viewcount(item, youtube_api)
        # if viewcount > views_threshold:
        title = find_title(item)
        video_url = find_video_url(item)
        channel_url = find_channel_url(item)
        channel_id = find_channel_id(item)
        channel_name = find_channel_title(item)
        num_subs = find_num_subscribers(item, channel_id, youtube_api)
        ratio = view_to_sub_ratio(viewcount, num_subs)
        days_since_published = how_old(item)
        score = custom_score(viewcount, ratio, days_since_published)
        df.loc[i] = [title, video_url, score, viewcount, channel_name, num_subs, ratio, channel_url]
        i += 1
    return df

def load_yaml(filepath):
    """Import YAML config file."""
    with open(filepath, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
