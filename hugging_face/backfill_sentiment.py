from dotenv import load_dotenv
import os
import requests
import psycopg

load_dotenv()
api_key = os.getenv("my_token")

url = "https://api-inference.huggingface.co/models/mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
headers = { "Authorization": f"Bearer {api_key}" }

def analyse_sentiment(text):
    #sending text to hugging face API for sentiment analysis
    if not api_key:
        print("API KEY not found, cannot analyze sentitment")
        return None, None # twice, becasue funtion is returning 2 values (a tuple) sentiment_label and sentiment score
    
    payload = {"inputs": [text]} #we pass fetched article title and pass it to hugging face
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() # when we get HTTP error (404, 500, 401 etc) program stops executing
        result = response.json()
        ## we're checking if the list has any elements in it
        # if result - is result none? len(result) >0 - is there an item in the list? len(result[0]) - is there a nested list? (hugging face retures a nested list)
        if result and len(result) > 0 and len(result[0]) >0:
            sentiment_label = result[0][0].get('label')
            sentiment_score = result[0][0].get('score')
            return sentiment_label, sentiment_score
        else:
            print(f"Empty or unexpected response for text: {text}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Error calling Hugging Face API for text '{text}': {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred during sentiment analysis: {e}")
        return None, None

def backfill_sentiment_data():
    """Fetches existing articles, analyzes sentiment, and updates the database."""
    db_conn_string = os.getenv("DB_CONN")
    if not db_conn_string:
        print("Database connection string not found")
        return
    
    try:
        with psycopg.connect(db_conn_string) as conn:
            with conn.cursor() as cur:

                 # Fetch articles that do NOT yet have sentiment data
                cur.execute("SELECT date, title FROM articles WHERE sentiment IS NULL;")
                articles = cur.fetchall() # Fetches (date, title) tuples
                print(f"Found {len(articles)} articles to process.")
                
                updates = []
                for date_obj, title in articles:
                    label, score = analyse_sentiment(title)
                    if label and score:
                        updates.append((label, score, date_obj))
                
                if updates:
                    cur.executemany(
                        "UPDATE articles SET sentiment = %s, sentiment_score = %s WHERE date = %s;",
                        updates
                    )
                    print(f"Updated {len(updates)} articles.")
                else:
                    print("No articles to update.")
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    backfill_sentiment_data()