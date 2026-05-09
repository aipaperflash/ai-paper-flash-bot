import os
import feedparser
import tweepy
from google import genai

try:
    # 1. 論文の取得 (arXiv)
    print("Fetching paper...")
    # 最もシンプルな検索クエリに変更
    feed_url = 'http://export.arxiv.org/api/query?search_query=all:ai&start=0&max_results=1'
    feed = feedparser.parse(feed_url)
    
    # もしヒットしなかった場合の予備クエリ
    if not feed.entries:
        print("Initial search failed. Trying broader search...")
        feed_url = 'http://export.arxiv.org/api/query?search_query=all:artificial+intelligence&start=0&max_results=1'
        feed = feedparser.parse(feed_url)

    if not feed.entries:
        print("No papers found even with broad search. Please check arXiv API status.")
    else:
        entry = feed.entries[0]
        title = entry.title
        summary = entry.summary
        link = entry.link
        print(f"Paper found: {title}")

        # 2. Geminiで要約とツイート作成
        print("Generating tweet...")
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        prompt = f"Create a catchy English tweet summarizing this AI paper. Keep it under 250 characters, use 1-2 hashtags, and make it engaging. No markdown formatting. \n\nTitle: {title}\nAbstract: {summary}"

        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        tweet_text = f"{response.text}\n{link}"

        # 3. Xへ投稿
        print("Posting to X...")
        x_client = tweepy.Client(
            bearer_token=os.environ["X_BEARER_TOKEN"],
            consumer_key=os.environ["X_API_KEY"],
            consumer_secret=os.environ["X_API_SECRET"],
            access_token=os.environ["X_ACCESS_TOKEN"],
            access_token_secret=os.environ["X_ACCESS_SECRET"]
        )
        x_client.create_tweet(text=tweet_text)
        print("Successfully posted to X!")

except Exception as e:
    print(f"Error occurred: {e}")
