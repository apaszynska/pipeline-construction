import os
import psycopg
import requests

def analyze_sentiment(text):
    api_key = os.getenv("my_token")
    url = "https://api-inference.huggingface.co/models/mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
    headers = { "Authorization": f"Bearer {api_key}" }

    if not api_key:
        print("API key missing for Hugging Face")
        return None, None
    
    try:
        response = requests.post(url, headers=headers, json={"inputs": [text]})
        response.raise_for_status()
        result = response.json()
        print(f"Sentiment response for '{text}': {result}")
        if result and result[0]:
            return result[0][0].get('label'), result[0][0].get('score')
        return None, None
    except Exception as e:
        print(f"Sentiment analysis error for {text}: {e}")
        return None, None


def update_ft_table(event, context):
    print("Received event:", event)
    try:
        db_conn = os.getenv("DB_CONN")
        if not db_conn:
            print("Database connection string missing!")
            return {"status":"error", "message": "DB_CONN missing"}
        with psycopg.connect(db_conn, prepare_threshold=None) as conn:
            with conn.cursor() as cur:
                articles = event.get("articles", [])
                
                values = []
                for article in articles:
                    sentiment_label, sentiment_score = analyze_sentiment(article["title"])
                    values.append((article["date"], article["title"], sentiment_label, sentiment_score))
                    print(f"Article: {article['title']} | Sentiment: {sentiment_label}, Score: {sentiment_score}")
                
                if values:
                    cur.executemany(
                        """INSERT INTO articles(date, title, sentiment, sentiment_score) 
                           VALUES (%s, %s, %s, %s) ON CONFLICT (date, title) DO NOTHING;""",
                        values
                    )
                    print(f"Processed {len(values)} articles")
                else:    
                    print("No artilcles to process")
                    
                return {"status": "success", "processed_articles": len(values)}
    
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}