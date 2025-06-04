import os
import psycopg

def update_ft_table(event, context):
    dbconn = os.getenv("DB_CONN")
    conn = psycopg.connect(dbconn)
    cur = conn.cursor()
    # exctract the list of articles from my event
    articles = event.get("articles",[])

    values = [(article["date"], article["title"]) for article in articles]

    cur.executemany(
        '''
            INSERT INTO articles(date, title)
            VALUES (%s, %s)
            ON CONFLICT (date) DO NOTHING;
        ''',
        values
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "success"}