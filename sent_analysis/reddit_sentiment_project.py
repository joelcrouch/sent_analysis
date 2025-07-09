import praw
import pandas as pd
import numpy as np
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import re
import json
from collections import Counter
import time

class RedditSentimentAnalyzer:
    def __init__(self, client_id, client_secret, user_agent):
        """Initialize Reddit API connection and sentiment analyzers"""
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.vader = SentimentIntensityAnalyzer()
        self.data = []
        
    def clean_text(self, text):
        """Clean and preprocess text"""
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?]', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()
    
    def analyze_sentiment(self, text):
        """Analyze sentiment using both TextBlob and VADER"""
        # TextBlob sentiment
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity
        textblob_subjectivity = blob.sentiment.subjectivity
        
        # VADER sentiment
        vader_scores = self.vader.polarity_scores(text)
        
        return {
            'textblob_polarity': textblob_polarity,
            'textblob_subjectivity': textblob_subjectivity,
            'vader_positive': vader_scores['pos'],
            'vader_negative': vader_scores['neg'],
            'vader_neutral': vader_scores['neu'],
            'vader_compound': vader_scores['compound']
        }
    
    def search_reddit(self, query, subreddit_list=None, limit=100, time_filter='month'):
        """Search Reddit for posts and comments"""
        print(f"Searching for: {query}")
        
        # Default subreddits to search
        if subreddit_list is None:
            subreddit_list = [
                'worldnews', 'news', 'travel', 'soccer', 'football', 
                'politics', 'geopolitics', 'UAE', 'Qatar', 'MiddleEast',
                'dubai', 'AskReddit', 'todayilearned'
            ]
        
        search_data = []
        
        for sub_name in subreddit_list:
            try:
                subreddit = self.reddit.subreddit(sub_name)
                print(f"Searching r/{sub_name}...")
                
                # Search posts
                for post in subreddit.search(query, limit=limit//len(subreddit_list), time_filter=time_filter):
                    # Skip if post is removed or deleted
                    if post.selftext == '[removed]' or post.selftext == '[deleted]':
                        continue
                    
                    # Combine title and selftext
                    full_text = f"{post.title} {post.selftext}".strip()
                    
                    if len(full_text) > 10:  # Skip very short posts
                        cleaned_text = self.clean_text(full_text)
                        sentiment = self.analyze_sentiment(cleaned_text)
                        
                        search_data.append({
                            'id': post.id,
                            'type': 'post',
                            'subreddit': sub_name,
                            'title': post.title,
                            'text': cleaned_text,
                            'score': post.score,
                            'upvote_ratio': post.upvote_ratio,
                            'num_comments': post.num_comments,
                            'created_utc': datetime.fromtimestamp(post.created_utc),
                            'url': post.url,
                            'query': query,
                            **sentiment
                        })
                
                # Add a small delay to respect rate limits
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error searching r/{sub_name}: {e}")
                continue
        
        return search_data
    
    def collect_data(self, countries=['UAE', 'Qatar'], limit_per_query=200):
        """Collect data for multiple countries/queries"""
        all_data = []
        
        # Define search queries for each country
        search_queries = {
            'UAE': ['UAE', 'United Arab Emirates', 'Dubai', 'Abu Dhabi'],
            'Qatar': ['Qatar', 'Doha', 'World Cup Qatar']
        }
        
        for country in countries:
            print(f"\n--- Collecting data for {country} ---")
            
            for query in search_queries.get(country, [country]):
                data = self.search_reddit(query, limit=limit_per_query)
                
                # Add country label
                for item in data:
                    item['country'] = country
                
                all_data.extend(data)
                
                # Rate limiting
                time.sleep(1)
        
        self.data = all_data
        return pd.DataFrame(all_data)
    
    def categorize_sentiment(self, compound_score):
        """Categorize sentiment based on compound score"""
        if compound_score >= 0.05:
            return 'Positive'
        elif compound_score <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'
    
    def analyze_data(self):
        """Analyze collected data"""
        if not self.data:
            print("No data to analyze. Please collect data first.")
            return None
        
        df = pd.DataFrame(self.data)
        
        # Add sentiment categories
        df['sentiment_category'] = df['vader_compound'].apply(self.categorize_sentiment)
        
        # Basic statistics
        print("\n=== SENTIMENT ANALYSIS RESULTS ===")
        print(f"Total posts analyzed: {len(df)}")
        print(f"Date range: {df['created_utc'].min()} to {df['created_utc'].max()}")
        
        # Sentiment distribution by country
        print("\n--- Sentiment Distribution by Country ---")
        sentiment_by_country = df.groupby(['country', 'sentiment_category']).size().unstack(fill_value=0)
        print(sentiment_by_country)
        
        # Average sentiment scores
        print("\n--- Average Sentiment Scores ---")
        avg_sentiment = df.groupby('country')[['vader_compound', 'textblob_polarity']].mean()
        print(avg_sentiment)
        
        # Top subreddits
        print("\n--- Top Subreddits by Posts ---")
        top_subreddits = df['subreddit'].value_counts().head(10)
        print(top_subreddits)
        
        return df
    
    def visualize_results(self, df):
        """Create visualizations"""
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Sentiment distribution by country
        sentiment_counts = df.groupby(['country', 'sentiment_category']).size().unstack(fill_value=0)
        sentiment_counts.plot(kind='bar', ax=axes[0,0], color=['red', 'gray', 'green'])
        axes[0,0].set_title('Sentiment Distribution by Country')
        axes[0,0].set_xlabel('Country')
        axes[0,0].set_ylabel('Number of Posts')
        axes[0,0].legend(title='Sentiment')
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # 2. Average sentiment scores
        avg_scores = df.groupby('country')['vader_compound'].mean()
        avg_scores.plot(kind='bar', ax=axes[0,1], color='skyblue')
        axes[0,1].set_title('Average Sentiment Score by Country')
        axes[0,1].set_xlabel('Country')
        axes[0,1].set_ylabel('Average VADER Compound Score')
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # 3. Sentiment over time
        df['date'] = df['created_utc'].dt.date
        sentiment_over_time = df.groupby(['date', 'country'])['vader_compound'].mean().unstack(fill_value=0)
        sentiment_over_time.plot(ax=axes[1,0], marker='o')
        axes[1,0].set_title('Sentiment Trend Over Time')
        axes[1,0].set_xlabel('Date')
        axes[1,0].set_ylabel('Average Sentiment Score')
        axes[1,0].legend(title='Country')
        
        # 4. Top subreddits
        top_subs = df['subreddit'].value_counts().head(8)
        top_subs.plot(kind='barh', ax=axes[1,1], color='lightcoral')
        axes[1,1].set_title('Top Subreddits by Number of Posts')
        axes[1,1].set_xlabel('Number of Posts')
        
        # Save charts with timestamp BEFORE showing
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chart_filename = f"{timestamp}_sentiment_charts.png"
        
        # Save the figure
        fig.savefig(chart_filename, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"Charts saved to {chart_filename}")


        plt.tight_layout()
        plt.show()
        # plt.savefig('sentiment_analysis_charts.png', dpi=300, bbox_inches='tight')
        return fig
    
    def save_results(self, df, filename=None):
        """Save results to CSV with timestamp"""
        if filename is None:
            # Create timestamp filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_reddit_sentiment.csv"
        
        df.to_csv(filename, index=False)
        print(f"Results saved to {filename}")
        return filename
    
    def get_sample_posts(self, df, country, sentiment='Positive', n=5):
        """Get sample posts for manual inspection"""
        filtered_df = df[(df['country'] == country) & (df['sentiment_category'] == sentiment)]
        sample = filtered_df.nlargest(n, 'vader_compound')[['title', 'text', 'vader_compound', 'subreddit']]
        
        print(f"\n=== Sample {sentiment} posts about {country} ===")
        for idx, row in sample.iterrows():
            print(f"\nSubreddit: r/{row['subreddit']}")
            print(f"Title: {row['title']}")
            print(f"Sentiment Score: {row['vader_compound']:.3f}")
            print(f"Text: {row['text'][:200]}...")
            print("-" * 50)
        
        return sample

# Example usage and setup
def main():
    """Main function to run the sentiment analysis"""
    
    # You need to set up your Reddit API credentials
    # Go to https://www.reddit.com/prefs/apps to create an app
    CLIENT_ID = 'k22u8I8qZebAMtAjTyILDg'
    CLIENT_SECRET = 'XPHWghHgJ8n_TLHkurBT5z_-FPSG3g'
    USER_AGENT = 'sentiment_analysis_bot_v1.0'
    
    # Initialize analyzer
    analyzer = RedditSentimentAnalyzer(CLIENT_ID, CLIENT_SECRET, USER_AGENT)
    
    print("Starting Reddit sentiment analysis for UAE and Qatar...")
    
    # Collect data
    df = analyzer.collect_data(countries=['UAE', 'Qatar'], limit_per_query=100)
    
    # Analyze results
    results_df = analyzer.analyze_data()
    
    if results_df is not None:
        # Create visualizations
        analyzer.visualize_results(results_df)
        
        # Save results
        analyzer.save_results(results_df)
        
        # Show sample posts
        analyzer.get_sample_posts(results_df, 'UAE', 'Positive', 3)
        analyzer.get_sample_posts(results_df, 'Qatar', 'Negative', 3)
        
        print("\nAnalysis complete! Check the CSV file for detailed results.")

if __name__ == "__main__":
    main()
