from datetime import datetime, timedelta
import aiohttp
import asyncio
from bs4 import BeautifulSoup as bs
import PySimpleGUI as sg

def validate_price(price):
    '''helper function to validate string from html is a valid stock price'''
    try:
        float(price.replace(',',''))
        return price # keep as a string
    except:
        return "n/a"


class StockSymbol:
    valid_date_format = "%b %d, %Y"

    def __init__(self, symbol: str):
        self.symbol = symbol.upper()
        self.valid = False
        self._open = False
        self._high = False
        self._low = False
        self._close = False
        self._date = False

    @property
    def date(self):
        return self._date
    @date.setter
    def date(self, new_date: str):
        try:
            self._date = datetime.strptime(new_date, self.valid_date_format)
        except ValueError:
            self._date = False
    
    @property
    def open(self):
        return self._open
    @open.setter
    def open(self, open_price: str):
        self._open = validate_price(open_price)

    @property
    def close(self):
        return self._close
    @close.setter
    def close(self, close_price: str):
        self._close = validate_price(close_price)

    @property
    def high(self):
        return self._high
    @high.setter
    def high(self, high_price: str):
        self._high = validate_price(high_price)

    @property
    def low(self):
        return self._low
    @low.setter
    def low(self, low_price: str):
        self._low = validate_price(low_price)


    def create_yf_url(self, cur_date: datetime, prev_date: datetime):
        '''create a historical prices yahoo finance url'''
        # attempt to cover at least 1 valid market-open day
        cur =  int(cur_date.timestamp())
        prev = int(prev_date.timestamp())
        # yahoo finance automatically returns a lookup page upon receipt of invalid symbol
        self.yf_url = f'https://finance.yahoo.com/quote/{self.symbol}/history?period1={prev}&period2={cur}&interval=1d'

    def extract_from_html(self, html: str):
        ''' extracts valid prices from a given html string returned from yahoo finance '''
        soup = bs(html, 'html.parser')
        table = soup.table
        
        # check to ensure symbol returns a page with historical prices
        if table is None or not table.has_attr('data-test'):
            print("table missing data-test attribute")
            self.valid = False
            return
        if table['data-test'] != 'historical-prices':
            print('invalid table data-test = '+table['data-test'])
            self.valid = False
            return
 
        self.valid = True

        data = ["n/a"]*5
        first_row = table.tbody.find('tr')
        if first_row is not None:
            spans = table.tbody.tr.find_all('span')
            if len(spans) > 4: # all or nothing
                data = [i.string for i in spans[:5]]

        self.date, self.open, self.high, self.low, self.close = data



async def fetch(session, symbol):
    print(symbol.yf_url)
    async with session.get(symbol.yf_url) as resp:
        assert resp.status == 200
        html = await resp.text()
        symbol.extract_from_html(html)


def create_stock_prices_layout(symbols: list[StockSymbol]) -> list[list]: 
    '''creates a new layout to display stock symbol prices'''
    heading = ["Symbol","Open", "High", "Low","Close"]
    rows = []
    invalid_symbols = []
    for symbol in symbols:
        row = []
        if symbol.valid:
            row.append(symbol.symbol)
            for price in [symbol.open, symbol.high, symbol.low, symbol.close]:
                row.append(price)
            rows.append(row)
        else:
            invalid_symbols.append(symbol.symbol)

    
    layout = []
    if invalid_symbols:
        invalids = "INVALID SYMBOLS: "+", ".join(invalid_symbols)
        layout.append([sg.Text(invalids, background_color='red')])
    
    layout += [
        [sg.Table(rows, headings=heading, num_rows=10)],
        [sg.OK(bind_return_key=True)]
    ]

    return layout


async def main():
    
    ######### create Main GUI window #########
    main_layout = [
            [sg.Text('Stock Symbols:'), sg.Input(metadata="comma separated symbols",key='symbols', do_not_clear=False)],
            [sg.Text('     enter multiple symbols as a comma separated list')],
            [sg.Button('Submit', bind_return_key=True), sg.Cancel()]
        ]
    main_window = sg.Window('Stock Price Data', main_layout)
    ###########################################


    ##### get and validate current date and time #####
    cur_date = datetime.utcnow()
    # attempt to ensure at least one open market day is covered
    prev_date = cur_date - timedelta(days=10)

    # check if the current date is on a weekend
    if cur_date.weekday() > 4:
        sg.popup('The Market is closed today! Prices displayed will be from most recent market-open day',
            auto_close=True, auto_close_duration = 4)

    # check to see if the United States based markets are open yet
    # 1430 relates to the NYSE opening bell based on UTC time
    elif (cur_date.hour*100+cur_date.minute)<1430:
        sg.popup('The market has not opened yet! Prices displayed will be from the most recent market-open day',
            auto_close=True, auto_close_duration = 4)
    #################################################


    headers = {"user-agent": "Mozilla/5.0"}
    async with aiohttp.ClientSession(headers=headers) as session:
        while True: # event loop
            event, value = main_window.read()
            if event in (sg.WIN_CLOSED, 'Cancel'):
                break

            symbols = set([s.strip().upper() for s in value['symbols'].split(',')]) #remove duplicates
            symbols = [StockSymbol(s) for s in symbols if s] # remove empty strings
            tasks = []
            for s in symbols:
                s.create_yf_url(cur_date, prev_date)
                tasks.append(fetch(session, s))
            
            await asyncio.gather(*tasks, return_exceptions = False)

            stock_prices_layout = create_stock_prices_layout(symbols)
            stock_market_date = symbols[0].date
            stock_prices_window = sg.Window(f"Stock Prices for {stock_market_date}", stock_prices_layout)
            event, value = stock_prices_window.read()
            if event == 'OK':
                stock_prices_window.close()

        main_window.close()
            

if __name__ == "__main__":
    from sys import platform

    if platform.startswith('win'):
        # appears to fix runtime error on windows machines
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())