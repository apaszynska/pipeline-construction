import os
import requests
import psycopg



def update_api_table(event, context):
    dbconn = os.getenv("DB_CONN")
    conn = psycopg.connect(dbconn)
    cur = conn.cursor()
    data = event
    insert_query = """
        INSERT INTO api_data (date, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (date) DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            volume = EXCLUDED.volume;
    """
    values = (
        data["date"],
        float(data["1. open"]),
        float(data["2. high"]),
        float(data["3. low"]),
        float(data["4. close"]),
        float(data["5. volume"])
    )
    cur.execute(insert_query, values)
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "success"}
