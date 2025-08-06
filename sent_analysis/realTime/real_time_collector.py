
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# It's better to import from the copied collectors and processor
from collectors.reddit_collector import collect_reddit_data
from collectors.bluesky_collector import collect_bluesky_data
from collectors.youtube_collector import collect_youtube_data
from processor.sentiment_analyzer import SentimentProcessor

def run_collection_cycle():
    """
    Runs a single cycle of data collection, processing, and saving.
    This function is designed to be called by a scheduler (like a cron job or GitHub Actions).
    """
    load_dotenv()
    print(f"--- Running data collection cycle at {datetime.utcnow().isoformat()} UTC ---")

    # --- Configuration ---
    # Load credentials from .env file or GitHub secrets
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "sentiment_analysis_bot_v1.0")
    BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
    BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

    queries = ['UAE', 'Qatar']
    all_data = []

    # --- Data Collection ---
    # Collect from Reddit
    if REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET:
        print("--- Collecting data from Reddit ---")
        for query in queries:
            try:
                reddit_data = collect_reddit_data(
                    client_id=REDDIT_CLIENT_ID,
                    client_secret=REDDIT_CLIENT_SECRET,
                    user_agent=REDDIT_USER_AGENT,
                    query=query,
                    limit=50
                )
                all_data.extend(reddit_data)
            except Exception as e:
                print(f"Error collecting from Reddit for query '{query}': {e}")
    else:
        print("Reddit credentials not found. Skipping Reddit.")

    # Collect from Bluesky
    if BLUESKY_HANDLE and BLUESKY_PASSWORD:
        print("--- Collecting data from Bluesky ---")
        for query in queries:
            try:
                bluesky_data = collect_bluesky_data(
                    bluesky_handle=BLUESKY_HANDLE,
                    bluesky_password=BLUESKY_PASSWORD,
                    query=query,
                    limit=50
                )
                all_data.extend(bluesky_data)
            except Exception as e:
                print(f"Error collecting from Bluesky for query '{query}': {e}")
    else:
        print("Bluesky credentials not found. Skipping Bluesky.")

    # Collect from YouTube
    if YOUTUBE_API_KEY:
        print("--- Collecting data from YouTube ---")
        for query in queries:
            try:
                youtube_data = collect_youtube_data(
                    api_key=YOUTUBE_API_KEY,
                    query=query,
                    max_videos=5,
                    max_comments_per_video=50
                )
                all_data.extend(youtube_data)
            except Exception as e:
                print(f"Error collecting from YouTube for query '{query}': {e}")
    else:
        print("YouTube API key not found. Skipping YouTube.")

    if not all_data:
        print("No data was collected in this cycle. Exiting.")
        return

    # --- Processing and Analysis ---
    processor = SentimentProcessor()
    results_df = processor.process_data(all_data)

    # --- Save Results ---
    output_csv_path = "/home/dev1/dev/sentimentAnalyis/sent_analysis/realTime/sentiment_data.csv"
    # Add a timestamp to the new data
    results_df['collection_timestamp_utc'] = datetime.utcnow()

    # Reorder columns to have the timestamp first
    cols = ['collection_timestamp_utc'] + [col for col in results_df.columns if col != 'collection_timestamp_utc']
    results_df = results_df[cols]

    # Append to CSV, creating it with a header if it doesn't exist
    try:
        if not os.path.exists(output_csv_path):
            results_df.to_csv(output_csv_path, index=False, mode='w', header=True)
            print(f"Created new data file at {output_csv_path}")
        else:
            results_df.to_csv(output_csv_path, index=False, mode='a', header=False)
            print(f"Appended {len(results_df)} new records to {output_csv_path}")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")

    print(f"--- Data collection cycle finished at {datetime.utcnow().isoformat()} UTC ---")

if __name__ == "__main__":
    run_collection_cycle()
