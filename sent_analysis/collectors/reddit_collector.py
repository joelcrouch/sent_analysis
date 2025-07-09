import praw
from datetime import datetime
import re
import time

def clean_text(text):
    """Clean and preprocess text"""
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[^\w\s.,!?]', '', text)
    text = ' '.join(text.split())
    return text.strip()

def collect_reddit_data(client_id, client_secret, user_agent, query, subreddit_list=None, limit=100, time_filter='month'):
    """Search Reddit for posts and comments"""
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )
    
    if subreddit_list is None:
        subreddit_list = [
            'worldnews', 'news', 'travel', 'soccer', 'football', 
            'politics', 'geopolitics', 'UAE', 'Qatar', 'MiddleEast',
            'dubai', 'AskReddit', 'todayilearned'
        ]
    
    search_data = []
    
    for sub_name in subreddit_list:
        try:
            subreddit = reddit.subreddit(sub_name)
            print(f"Searching r/{sub_name} for '{query}'...")
            
            for post in subreddit.search(query, limit=limit//len(subreddit_list), time_filter=time_filter):
                if post.selftext == '[removed]' or post.selftext == '[deleted]':
                    continue
                
                full_text = f"{post.title} {post.selftext}".strip()
                
                if len(full_text) > 10:
                    cleaned_text = clean_text(full_text)
                    
                    search_data.append({
                        'source': 'Reddit',
                        'id': post.id,
                        'text': cleaned_text,
                        'author': post.author.name if post.author else '[deleted]',
                        'created_at': datetime.fromtimestamp(post.created_utc),
                        'source_specific_metrics': {
                            'score': post.score,
                            'upvote_ratio': post.upvote_ratio,
                            'num_comments': post.num_comments,
                            'subreddit': sub_name
                        },
                        'query': query
                    })
            
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Error searching r/{sub_name}: {e}")
            continue
            
    return search_data
