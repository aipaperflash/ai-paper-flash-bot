import os
import feedparser
import tweepy
import requests
import json

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

    # 2. Gemini APIの直接呼び出し（SDKのバグを完全回避）
    print("Generating tweet...")
    api_key = os.environ["GEMINI_API_KEY"]
    # ライブラリを通さず、直接URLを叩きます
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = f"Create a catchy English tweet summarizing this AI paper. Keep it under 250 characters, use 1-2 hashtags, and make it engaging. \n\nTitle: {title}\nAbstract: {summary}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    # 直接通信を実行
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        result = response.json()
        ai_text = result['candidates'][0]['content']['parts'][0]['text']
        tweet_text = f"{ai_text}\n{link}"
        print("Gemini generation successful!")
    else:
        # 💥 【無敵モード】万が一Geminiがエラーになっても、強制的にXへの投稿をテストする
        print(f"Gemini API Error: {response.text}")
        print("Using fallback generic tweet to test X posting...")
        tweet_text = f"Exploring new trends in AI! Check out this paper: {title}\n{link} #AI #Research"

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
