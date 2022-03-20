from datetime import datetime, timedelta
import time
import aiohttp
import asyncio
from bs4 import BeautifulSoup as bs


async def fetch(client, ticker):
        # guarantee we get at least 1 valid market opening day
        cur = datetime.today()
        prev = cur - timedelta(days=10)
        cur =  str(int(cur.timestamp()))
        prev = str(int(prev.timestamp()))
        yahoo_finance_url = f'https://finance.yahoo.com/quote/{ticker}/history?period1={prev}&period2={cur}&interval=1d'
        print(yahoo_finance_url)
        async with client.get(yahoo_finance_url) as resp:
            assert resp.status == 200
            return await resp.text()

def extract_ticker_prices(html):
    soup = bs(html, 'html.parser')
    historical_data = soup.find_all('tbody')
    if len(historical_data) < 1:
        print("no tbody")
        return
    spans = historical_data[0].find_all('span')
    if len(spans) < 5:
        print(f"not enough spans. found {len(spans)}")
        return
    
    date,open,high,low,close = (i.string for i in spans[:5])
    return date,open,high,low,close
    



async def main(tickers):

    headers = {"user-agent": "Mozilla/5.0"}
    async with aiohttp.ClientSession( headers=headers) as session:
        tasks = [fetch(session, ticker) for ticker in tickers]
        htmls = await asyncio.gather(*tasks, return_exceptions = True)
        
    for ticker, html in zip(tickers,htmls):
        try:
            d,o,h,l,c = extract_ticker_prices(html)
            print(f"prices for {ticker}\nmost recent date: {d}\nhigh price: {h}\nlow price: {l}\nopen price:{o}\nclose price: {c}\n")
        except Exception as e:
            print(e)
            print(f"Could not get data for ticker {ticker}")

if __name__ == "__main__":
    from sys import platform

    if platform.startswith('win'):
        # appears to fix runtime error on windows machines
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main(['ISRG','GME','SOFI']))