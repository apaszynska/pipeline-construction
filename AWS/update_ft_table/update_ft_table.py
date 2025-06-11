import os
import psycopg
import requests

api_key = os.getenv("my_token")
url = "https://api-inference.huggingface.co/models/mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
headers = { "Authorization": f"Bearer {api_key}" }

def analyze_sentiment(text):
    if not api_key:
        return None, None
    
    try:
        response = requests.post(url, headers=headers, json={"inputs": [text]})
        response.raise_for_status()
        result = response.json()
        
        if result and result[0]:
            return result[0][0].get('label'), result[0][0].get('score')
        return None, None
    except Exception as e:
        print(f"Sentiment analysis error: {e}")
        return None, None

def update_ft_table(event, context):
    try:
        with psycopg.connect(os.getenv("DB_CONN")) as conn:
            with conn.cursor() as cur:
                articles = event.get("articles", [])
                
                values = []
                for article in articles:
                    sentiment_label, sentiment_score = analyze_sentiment(article["title"])
                    values.append((article["date"], article["title"],article["link"], sentiment_label, sentiment_score))
                
                if values:
                    cur.executemany(
                        """INSERT INTO articles(date, title, link,sentiment, sentiment_score) 
                           VALUES (%s, %s, %s, %s. %s) ON CONFLICT (date) DO NOTHING;""",
                        values
                    )
                    print(f"Processed {len(values)} articles")
                
                return {"status": "success", "processed_articles": len(values)}
    
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}