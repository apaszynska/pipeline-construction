import datetime
import os
import requests
import bs4

def scrape_data(event, context):

    url = 'https://u.today/search/node?keys=bitcoin'
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    

    articles = soup.find_all("div", attrs ={"class": "news__item"})

    results = []
    dates = []

    for article in articles:
        title_div = article.find("div", attrs = {"class": "news__item-title"})
        date_div = article.find("div", attrs = {"class":"humble"})

        if title_div and date_div:
            title = title_div.get_text(strip = True)
            date = date_div.get_text(strip = True)
            try:
                date_obj = datetime.datetime.strptime(date, "%b %d, %Y - %H:%M") #converting each date string immediately into a datetime object and store in dates list
                results.append((date_obj, title))
                dates.append(date_obj)
            except ValueError:
                print(f"Skipping the article due to unrecognized date format")

        #the dates[] is populated only if date and titlle found in article[], so the date can be parsed into a datetime object, if strptime fails, the append op are skipped
    if not dates: #if the list is empty then...
        print("No articles found")
        return {"date_scraped": None, "articles": []}  #needed for finding the lastest date
    
    today = datetime.datetime.today().date()
    # Try to find articles from today - if date=today then for date,time in our results we create a new list of tuples
    todays_articles = [(d, t) for d, t in results if d.date() == today]

    if not todays_articles:
        latest_date = max(dates)
        todays_articles = [(d, t) for d, t in results if d.date() == latest_date.date()]
        print(f"No articles from today. Showing most recent articles from {latest_date.strftime('%b %d, %Y')}:")
    
    # Format articles as list of dicts
    articles_list = [{"date": d.strftime("%Y-%m-%d %H:%M"), "title": t} for d, t in todays_articles]

    return {
        "date_scraped": today.strftime("%Y-%m-%d"),
        "articles": articles_list
    }