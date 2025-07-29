import pandas as pd
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class SentimentProcessor:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()

    def analyze_sentiment(self, text):
        """Analyze sentiment using both TextBlob and VADER"""
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity
        textblob_subjectivity = blob.sentiment.subjectivity
        
        vader_scores = self.vader.polarity_scores(text)
        
        return {
            'textblob_polarity': textblob_polarity,
            'textblob_subjectivity': textblob_subjectivity,
            'vader_positive': vader_scores['pos'],
            'vader_negative': vader_scores['neg'],
            'vader_neutral': vader_scores['neu'],
            'vader_compound': vader_scores['compound']
        }

    def categorize_sentiment(self, compound_score):
        """Categorize sentiment based on compound score"""
        if compound_score >= 0.05:
            return 'Positive'
        elif compound_score <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'

    def process_data(self, data):
        """Process a list of dictionaries into a DataFrame with sentiment scores"""
        df = pd.DataFrame(data)
        if df.empty:
            return df

        sentiment_df = df['text'].apply(lambda text: pd.Series(self.analyze_sentiment(text)))
        df = pd.concat([df, sentiment_df], axis=1)
        df['sentiment_category'] = df['vader_compound'].apply(self.categorize_sentiment)
        return df

    def analyze_and_visualize(self, df):
        """Perform and print main analysis and generate visualizations"""
        if df.empty:
            print("DataFrame is empty. No analysis to perform.")
            return

        print("\n=== SENTIMENT ANALYSIS RESULTS ===")
        print(f"Total posts analyzed: {len(df)}")
        
        print("\n--- Sentiment Distribution by Query ---")
        sentiment_by_query = df.groupby(['query', 'sentiment_category']).size().unstack(fill_value=0)
        print(sentiment_by_query)

        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # 1. Sentiment distribution by query
        sentiment_counts = df.groupby(['query', 'sentiment_category']).size().unstack(fill_value=0)
        sentiment_counts.plot(kind='bar', ax=axes[0, 0], color=['red', 'gray', 'green'])
        axes[0, 0].set_title('Sentiment Distribution by Query')
        axes[0, 0].set_xlabel('Query')
        axes[0, 0].set_ylabel('Number of Posts')
        axes[0, 0].legend(title='Sentiment')
        axes[0, 0].tick_params(axis='x', rotation=45)

        # 2. Average sentiment scores by query
        avg_scores = df.groupby('query')['vader_compound'].mean()
        avg_scores.plot(kind='bar', ax=axes[0, 1], color='skyblue')
        axes[0, 1].set_title('Average Sentiment Score by Query')
        axes[0, 1].set_xlabel('Query')
        axes[0, 1].set_ylabel('Average VADER Compound Score')
        axes[0, 1].tick_params(axis='x', rotation=45)

        # 3. Sentiment over time
        df['date'] = pd.to_datetime(df['created_at'], utc=True).dt.date
        sentiment_over_time = df.groupby(['date', 'query'])['vader_compound'].mean().unstack(fill_value=0)
        sentiment_over_time.plot(ax=axes[1, 0], marker='o')
        axes[1, 0].set_title('Sentiment Trend Over Time')
        axes[1, 0].set_xlabel('Date')
        axes[1, 0].set_ylabel('Average Sentiment Score')
        axes[1, 0].legend(title='Query')

        # 4. Sentiment by Source
        df['query_source'] = df['query'] + ' - ' + df['source']
        sentiment_by_source = df.groupby(['query_source', 'sentiment_category']).size().unstack(fill_value=0)
        sentiment_by_source.plot(kind='bar', ax=axes[1, 1], colormap='viridis')
        axes[1, 1].set_title('Sentiment Distribution by Source')
        axes[1, 1].set_xlabel('Query and Source')
        axes[1, 1].set_ylabel('Number of Posts')
        axes[1, 1].legend(title='Sentiment')
        axes[1, 1].tick_params(axis='x', rotation=45)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chart_filename = f"{timestamp}_sentiment_charts.png"
        
        fig.savefig(chart_filename, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"Charts saved to {chart_filename}")

        plt.tight_layout()
        plt.show()

    def create_detailed_trend_chart(self, df):
        """Create a more detailed sentiment trend chart with a rolling average."""
        if df.empty or 'created_at' not in df.columns:
            return

        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(18, 10))

        # Ensure 'date' column exists
        if 'date' not in df.columns:
            df['date'] = pd.to_datetime(df['created_at'], utc=True).dt.date
        
        sentiment_over_time = df.groupby(['date', 'query'])['vader_compound'].mean().unstack()

        if sentiment_over_time.empty:
            print("No time-series data to plot for detailed trend chart.")
            return

        # Plot original daily data for each query
        for query in sentiment_over_time.columns:
            ax.plot(sentiment_over_time.index, sentiment_over_time[query], marker='o', linestyle='-', alpha=0.5, label=f'{query} (Daily)')

        # Plot 7-day rolling average for each query
        for query in sentiment_over_time.columns:
            rolling_avg = sentiment_over_time[query].rolling(window=7, min_periods=1).mean()
            ax.plot(sentiment_over_time.index, rolling_avg, linestyle='--', linewidth=2.5, label=f'{query} (7-Day Avg)')

        ax.set_title('Detailed Sentiment Trend Over Time', fontsize=20)
        ax.set_xlabel('Date', fontsize=14)
        ax.set_ylabel('Average VADER Compound Score', fontsize=14)
        
        # Improve legend
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, title='Query', bbox_to_anchor=(1.05, 1), loc='upper left')

        ax.axhline(0, color='black', linewidth=0.8, linestyle='--') # Add a line for neutral sentiment

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chart_filename = f"{timestamp}_detailed_sentiment_trend.png"
        
        try:
            fig.savefig(chart_filename, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"Detailed trend chart saved to {chart_filename}")
        except Exception as e:
            print(f"Error saving detailed trend chart: {e}")

        plt.tight_layout()
        plt.show()

    

    def save_results(self, df, filename=None):
        """Save results to CSV with timestamp"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_combined_sentiment.csv"
        
        df.to_csv(filename, index=False)
        print(f"Results saved to {filename}")
