# Social Media Sentiment Analysis

This project collects social media data from Reddit, Bluesky, and YouTube for specific queries (e.g., 'UAE', 'Qatar'), performs sentiment analysis, and visualizes the results. The output includes various charts and a CSV file containing the analyzed data.

## Features

*   **Multi-platform Data Collection:** Gathers posts and comments from Reddit, Bluesky, and YouTube.
*   **Sentiment Analysis:** Utilizes VADER and TextBlob for comprehensive sentiment scoring.
*   **Data Visualization:** Generates charts illustrating sentiment distribution, average sentiment scores, and trends over time.
*   **CSV Export:** Saves all processed data, including sentiment scores, to a CSV file.

## Getting Started

Follow these instructions to set up and run the sentiment analysis.

### Prerequisites

*   Python 3.9+
*   API credentials for:
    *   **Reddit:** `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` (obtain from Reddit API)
    *   **Bluesky:** `BLUESKY_HANDLE`, `BLUESKY_PASSWORD` (your Bluesky login details)
    *   **YouTube:** `YOUTUBE_API_KEY` (obtain from Google Cloud Console)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/social-sentiment-analysis.git
    cd social-sentiment-analysis
    ```
2.  **Set up a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: `venv\Scripts\activate`
    pip install -r requirements.txt
    ```
3.  **Configure environment variables:**
    Create a `.env` file in the root directory of the project and add your API credentials:
    ```
    REDDIT_CLIENT_ID="your_reddit_client_id"
    REDDIT_CLIENT_SECRET="your_reddit_client_secret"
    REDDIT_USER_AGENT="your_reddit_user_agent"

    BLUESKY_HANDLE="your_bluesky_handle"
    BLUESKY_PASSWORD="your_bluesky_password"

    YOUTUBE_API_KEY="your_youtube_api_key"
    ```
    *Note: If any credentials are missing, the script will skip data collection for that platform.*

### Running the Analysis

Execute the `main.py` script to collect data, perform sentiment analysis, and generate visualizations:

```bash
python main.py
```

## Output

Upon successful execution, the script will:

*   Display sentiment analysis summaries in the console.
*   Generate one or more PNG image files (e.g., `YYYYMMDD_HHMMSS_sentiment_charts.png`, `YYYYMMDD_HHMMSS_detailed_sentiment_trend.png`) containing various sentiment distribution and trend charts. These files will be saved in the project's root directory.
*   Generate a CSV file (e.g., `YYYYMMDD_HHMMSS_combined_sentiment.csv`) containing all collected and processed data, including sentiment scores for each entry. This file will also be saved in the project's root directory.
*   Open a matplotlib window displaying the generated charts.

## Technical Stack (Core)

*   **Language:** Python 3.9+
*   **Data Analysis:** Pandas, NumPy
*   **Sentiment Analysis:** VADER Sentiment, TextBlob
*   **Data Visualization:** Matplotlib, Seaborn
*   **API Clients:** PRAW (for Reddit), ATProto (for Bluesky), Google API Client (for YouTube)
*   **Environment Management:** `python-dotenv`
