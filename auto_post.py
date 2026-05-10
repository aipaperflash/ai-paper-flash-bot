import os
import feedparser
import tweepy
import google.generativeai as genai

try:
    # 1. 論文の取得 (arXiv)
    print("Fetching paper...")
    feed_url = 'http://export.arxiv.org/api/query?search_query=all:ai&start=0&max_results=1'
    feed = feedparser.parse(feed_url)
    
    if not feed.entries:
        print("arXiv API no response. Using test data...")
        title = "Foundations of GenIR"
        summary = "This paper explores the fundamental principles of Generative Information Retrieval."
        link = "https://arxiv.org/abs/2401.00001"
    else:
        entry = feed.entries[0]
        title = entry.title
        summary = entry.summary
        link = entry.link
    
    print(f"Target Paper: {title}")

    # 2. Geminiで要約 (安定版の google-generativeai を使用)
    print("Generating tweet...")
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    # 古いライブラリではこの書き方が最も確実です
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"Create a catchy English tweet summarizing this AI paper. Keep it under 250 characters, use 1-2 hashtags, and make it engaging. \n\nTitle: {title}\nAbstract: {summary}"
    
    response = model.generate_content(prompt)
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
