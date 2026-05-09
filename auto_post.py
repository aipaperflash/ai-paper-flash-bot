import os
import feedparser
import tweepy
import google.generativeai as genai

# ==========================================
# 1. arXiv APIから最新論文を取得するモジュール
# ==========================================
def fetch_latest_paper():
    # cs.AI (Computer Science - AI) の最新論文を1件取得
    url = 'http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=1'
    feed = feedparser.parse(url)
    
    if not feed.entries:
        raise Exception("論文データの取得に失敗しました")
        
    paper = feed.entries[0]
    return {
        "title": paper.title,
        "summary": paper.summary,
        "link": paper.link
    }

# ==========================================
# 2. AI（Gemini API）で要約＆ポスト生成モジュール
# ==========================================
def generate_tweet(paper_data):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    以下の学術論文のタイトルと要約を元に、アメリカのテック層やエンジニア向けにX（Twitter）でバズる英語のポストを作成してください。
    
    【条件】
    - 専門用語を適切に使い、ビジネスや開発におけるインパクトを強調すること。
    - 250文字以内に収めること。
    - 最後に #AIPaper #MachineLearning のハッシュタグをつけること。
    - 返答は生成したポストのテキストのみ出力すること。
    
    【論文データ】
    Title: {paper_data['title']}
    Summary: {paper_data['summary']}
    """
    
    response = model.generate_content(prompt)
    
    # 最後に論文のリンクを付与して返す
    tweet_text = f"{response.text.strip()}\n\nLink: {paper_data['link']}"
    return tweet_text

# ==========================================
# 3. X (Twitter) への自動投稿モジュール
# ==========================================
def post_to_x(tweet_text):
    client = tweepy.Client(
        bearer_token=os.environ["X_BEARER_TOKEN"],
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_SECRET"]
    )
    
    response = client.create_tweet(text=tweet_text)
    print(f"Post successful! https://twitter.com/user/status/{response.data['id']}")

# ==========================================
# メイン処理
# ==========================================
if __name__ == "__main__":
    try:
        print("Fetching paper...")
        paper = fetch_latest_paper()
        
        print("Generating tweet...")
        tweet = generate_tweet(paper)
        
        print("Posting to X...")
        post_to_x(tweet)
        
    except Exception as e:
        print(f"Error occurred: {e}")
