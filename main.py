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

async def main():
    # Read the CSV file
    csv_filename = "test.csv"  # Replace with the actual filename
    with open(csv_filename, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            ean = row['EAN']
            articles = await get_price_from_google(ean)
            cheapest_articles = get_cheapest_articles(articles)
            print(f"EAN: {ean}")
            for cheapest_article in cheapest_articles:
                print(f"Price: {cheapest_article['price']}, Link: {cheapest_article['link']}")
            # for article in articles:
    # articles = await get_price_from_google("4008789701466")
    # for article in articles:
    #     print(f"Price: {article['price']}, Link: {article['link']}")
    # cheapest_article = get_cheapest_article(articles)
    # print(f"Price: {cheapest_article['price']}, Link: {cheapest_article['link']}")
    
    # print(articles)

asyncio.run(main())