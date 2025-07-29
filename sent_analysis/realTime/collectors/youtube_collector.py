from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
import re
import time

def clean_text(text):
    """Clean and preprocess text"""
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[^\w\s.,!?]', '', text)
    text = ' '.join(text.split())
    return text.strip()

def collect_youtube_data(api_key, query, max_videos=5, max_comments_per_video=50):
    """Search YouTube for videos and collect comments"""
    youtube = build('youtube', 'v3', developerKey=api_key)
    search_data = []

    print(f"Searching YouTube for videos related to '{query}'...")
    try:
        # Search for videos
        video_response = youtube.search().list(
            q=query,
            part='id,snippet',
            type='video',
            maxResults=max_videos
        ).execute()

        video_ids = [item['id']['videoId'] for item in video_response.get('items', [])]

        for video_id in video_ids:
            try:
                print(f"  Collecting comments for video ID: {video_id}")
                # Get comments for each video
                comments_response = youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    textFormat='plainText',
                    maxResults=max_comments_per_video
                ).execute()

                for item in comments_response.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet']
                    full_text = comment['textDisplay']
                    
                    if len(full_text) > 10:
                        cleaned_text = clean_text(full_text)
                        search_data.append({
                            'source': 'YouTube',
                            'id': item['id'],
                            'text': cleaned_text,
                            'author': comment['authorDisplayName'],
                            'created_at': datetime.fromisoformat(comment['publishedAt'].replace('Z', '+00:00')),
                            'source_specific_metrics': {
                                'video_id': video_id,
                                'like_count': comment['likeCount'],
                            },
                            'query': query
                        })
                time.sleep(0.1) # Small delay to respect rate limits
            except HttpError as e:
                if e.resp.status == 403 and 'commentsDisabled' in str(e.content):
                    print(f"  Comments are disabled for video {video_id}. Skipping.")
                    continue
                else:
                    print(f"An HttpError occurred: {e}")

    except Exception as e:
        print(f"Error collecting YouTube data: {e}")

    return search_data
