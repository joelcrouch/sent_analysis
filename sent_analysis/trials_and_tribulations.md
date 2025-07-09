# Trials & Tribulations Log

This document logs the errors encountered during development, the attempts made to resolve them, and the final working solutions. It also summarizes key architectural decisions and changes made throughout the project.

---

## Project Evolution & Architectural Decisions

**Initial State:**
Began with a monolithic `reddit_sentiment_project.py` script that handled both data collection from Reddit and sentiment analysis/visualization.

**Decision: Modular Architecture (Collectors, Processor, Main)**
To support multiple social media platforms and improve maintainability, the project was refactored into a modular structure:
-   `collectors/`: Dedicated modules for each social media platform (e.g., `reddit_collector.py`, `bluesky_collector.py`). Each collector is responsible *only* for fetching data from its respective API and returning it in a standardized format.
-   `processor/sentiment_analyzer.py`: A single module responsible for all sentiment analysis, data processing, and visualization, independent of the data source.
-   `main.py`: An orchestrator script that loads credentials, calls various collectors, collates their data, and then passes the combined data to the processor.

**Reasoning:**
-   **Scalability:** Easily add new social media platforms by creating new collector modules without modifying core analysis logic.
-   **Maintainability:** Clear separation of concerns makes code easier to understand, debug, and update.
-   **Reusability:** Sentiment analysis and visualization logic can be reused across all data sources.

**Decision: Standardized Data Format**
All collector modules were designed to return data in a consistent list of dictionaries, each containing common keys like `source`, `text`, `author`, `created_at`, and a nested `source_specific_metrics` dictionary for platform-specific data.

**Decision: Comparative Sentiment Analysis (by Query)**
Initially, the sentiment analysis grouped results by `source` (e.g., 'Reddit'). To enable direct comparison of sentiment for specific topics (e.g., 'UAE' vs. 'Qatar') across all collected data, the `SentimentProcessor` was modified to group and visualize results by the `query` field instead of the `source` field.

**Decision: Skipping X/Twitter Collector (API Limitations)**
After evaluating the current X/Twitter API landscape, it was decided to skip implementing a collector for this platform due to:
-   Highly restrictive free-tier limits (1,500 tweets/month).
-   Complex and potentially costly paid tiers.
-   The small sample size from the free tier would likely skew sentiment analysis results.

---

## Errors & Solutions Log

**1. Reddit API 401 Unauthorized Error**

**Symptom:**
`received 401 HTTP response` when trying to collect data from Reddit. This occurred consistently when the agent ran the script, but the user reported it working locally.

**Attempted Solutions:**
1.  Initial assumption: Incorrect `REDDIT_CLIENT_ID` or `REDDIT_CLIENT_SECRET` in `.env` file.
2.  Checked and confirmed the credentials in the `.env` file.
3.  Discovered and removed a trailing space in `REDDIT_CLIENT_ID` in the `.env` file.

**Solution:**
While removing the trailing space was a good fix for a potential issue, the core problem for the agent's execution was likely an environmental difference or a subtle credential mismatch that was not immediately apparent. The user's local execution confirmed the code logic was sound. The issue was bypassed by focusing on the user's successful local execution.

---

**2. Bluesky API `missing 1 required positional argument: 'params'` Error**

**Symptom:**
`TypeError: AppBskyFeedNamespace.search_posts() missing 1 required positional argument: 'params'` when calling the Bluesky `search_posts` method.

**Attempted Solutions:**
1.  Initial call was `client.app.bsky.feed.search_posts(q=query, limit=limit)`.

**Solution:**
The `atproto` library's `search_posts` method requires parameters to be passed within a `params` dictionary. The call was corrected to `client.app.bsky.feed.search_posts(params={'q': query, 'limit': limit})` in `collectors/bluesky_collector.py`.

---

**3. Bluesky API `'PostView' object has no attribute 'text'` Error**

**Symptom:**
`'PostView' object has no attribute 'text'` when trying to access the text content of a Bluesky post.

**Attempted Solutions:**
1.  Initial access was `post.text`.

**Solution:**
The text content of a Bluesky post is nested within the `record` attribute of the `PostView` object. The access was corrected to `post.record.text` in `collectors/bluesky_collector.py`.

---

**4. Pandas `ValueError: Tz-aware datetime.datetime cannot be converted to datetime64 unless utc=True`**

**Symptom:**
`ValueError: Tz-aware datetime.datetime cannot be converted to datetime64 unless utc=True, at position X` when converting the `created_at` column to datetime objects in `sentiment_analyzer.py`.

**Attempted Solutions:**
1.  Initial conversion was `pd.to_datetime(df['created_at']).dt.date`.

**Solution:**
Timestamps from Bluesky (and potentially other sources) are timezone-aware. Pandas requires explicit handling for these. The conversion was corrected to `pd.to_datetime(df['created_at'], utc=True).dt.date` in `processor/sentiment_analyzer.py`.