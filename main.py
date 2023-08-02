import httpx
import asyncio
from bs4 import BeautifulSoup
import re
import csv

def extract_numbers_from_list(data_list):
    number = int()
    if data_list:
        for item in data_list:
            matches = re.findall(r"\b\d+\,\d+ €", str(item))
            if matches:
                for match in matches:
                    number = match.replace(",", ".")[:-2]  # Replace comma with dot for float conversion
        return number
    else:
        return False
    
def get_cheapest_articles(articles):
    # Sort articles by price in ascending order
    sorted_articles = sorted(articles, key=lambda x: x['price'])

    # Get the three cheapest articles (first three elements in the sorted list)
    cheapest_articles = sorted_articles[:3]

    return cheapest_articles

async def get_price_from_google(ean):
    url = f"https://www.google.com/search?q={ean}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4703.0 Safari/537.36"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        articles = []
        i = 0

        for el in soup.select('div.MjjYud:not(div.ULSxyf div.MjjYud)'):

            i+=1
            for div in el:
                div_content = div.find('div', class_='fG8Fp uo4vr')
                price = extract_numbers_from_list(div_content)
                if not price:
                    continue

                anchor_tag = div.find('a')  # Find the first anchor tag inside the div (if exists)
                if anchor_tag:
                    link = anchor_tag.get('href')
                else:
                    continue
                
                articles.append({
                    "price": price,
                    "link": link
                })

        return articles
    
async def get_articles(csv_reader):
        cheapest_articles = []
        for row in csv_reader:
            ean = row['EAN']
            articles = await get_price_from_google(ean)
            cheapest_articles.append({
                'ean': ean,
                'articles' : get_cheapest_articles(articles)
            })
        return cheapest_articles

async def main():
    # Read the CSV file
    csv_filename = "test.csv"
    with open(csv_filename, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        articles = await get_articles(csv_reader)
        for article in articles:
            print(f"EAN: {article['ean']}")
            for a in article['articles']:
                print(f"Price: {a['price']}, Link: {a['link']}")

asyncio.run(main())