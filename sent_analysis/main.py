import os
from dotenv import load_dotenv
from collectors.reddit_collector import collect_reddit_data
from collectors.bluesky_collector import collect_bluesky_data
from collectors.youtube_collector import collect_youtube_data

from processor.sentiment_analyzer import SentimentProcessor

def main():
    """Main function to orchestrate the data collection and analysis"""
    load_dotenv()

    # --- Configuration ---
    # Load Reddit credentials from .env file
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "sentiment_analysis_bot_v1.0")

    # Define your search queries
    queries = ['UAE', 'Qatar']
    
    # --- Data Collection ---
    all_data = []
    
    # Collect from Reddit
    if REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET:
        print("--- Collecting data from Reddit ---")
        for query in queries:
            reddit_data = collect_reddit_data(
                client_id=REDDIT_CLIENT_ID, 
                client_secret=REDDIT_CLIENT_SECRET, 
                user_agent=REDDIT_USER_AGENT,
                query=query,
                limit=50 # Limit per query for faster testing
            )
            all_data.extend(reddit_data)
    else:
        print("Reddit credentials not found. Skipping Reddit.")

    # Load Bluesky credentials from .env file
    BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
    BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")

    # Collect from Bluesky
    if BLUESKY_HANDLE and BLUESKY_PASSWORD:
        print("\n--- Collecting data from Bluesky ---")
        for query in queries:
            bluesky_data = collect_bluesky_data(
                bluesky_handle=BLUESKY_HANDLE,
                bluesky_password=BLUESKY_PASSWORD,
                query=query,
                limit=50 # Limit per query for faster testing
            )
            all_data.extend(bluesky_data)
    else:
        print("Bluesky credentials not found. Skipping Bluesky.")

    # Load YouTube credentials from .env file
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

    # Collect from YouTube
    if YOUTUBE_API_KEY:
        print("\n--- Collecting data from YouTube ---")
        for query in queries:
            youtube_data = collect_youtube_data(
                api_key=YOUTUBE_API_KEY,
                query=query,
                max_videos=5,
                max_comments_per_video=50
            )
            all_data.extend(youtube_data)
    else:
        print("YouTube API key not found. Skipping YouTube.")

    if not all_data:
        print("No data was collected. Exiting.")
        return

    # --- Processing and Analysis ---
    processor = SentimentProcessor()
    
    # Process the raw data into a DataFrame with sentiment scores
    results_df = processor.process_data(all_data)
    
    # Perform the main analysis and generate charts
    processor.analyze_and_visualize(results_df)
    processor.create_detailed_trend_chart(results_df)
    
    
    
    # Save the final results to a CSV
    processor.save_results(results_df)
    
    print("\nAnalysis complete! Check the CSV and PNG files for results.")

if __name__ == "__main__":
    main()
