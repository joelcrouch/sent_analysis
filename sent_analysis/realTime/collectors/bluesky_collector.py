from atproto import Client
from datetime import datetime
import re
import time

def clean_text(text):
    """Clean and preprocess text"""
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[^\w\s.,!?]', '', text)
    text = ' '.join(text.split())
    return text.strip()

def collect_bluesky_data(bluesky_handle, bluesky_password, query, limit=100):
    """Search Bluesky for posts"""
    client = Client()
    try:
        client.login(bluesky_handle, bluesky_password)
    except Exception as e:
        print(f"Error logging into Bluesky: {e}")
        return []

    search_data = []
    print(f"Searching Bluesky for '{query}'...")
    
    try:
        response = client.app.bsky.feed.search_posts(params={'q': query, 'limit': limit})
        for post in response.posts:
            cleaned_text = clean_text(post.record.text)
            if len(cleaned_text) > 10:
                search_data.append({
                    'source': 'Bluesky',
                    'id': post.uri,
                    'text': cleaned_text,
                    'author': post.author.handle,
                    'created_at': datetime.fromisoformat(post.indexed_at),
                    'source_specific_metrics': {
                        'reply_count': post.reply_count,
                        'repost_count': post.repost_count,
                        'like_count': post.like_count,
                    },
                    'query': query
                })
    except Exception as e:
        print(f"Error searching Bluesky: {e}")
        
    return search_data
