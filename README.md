# stock_ticker_scraper
a program that takes in stock ticker symbols and returns the daily open, close, high and low prices, as reported by yahoo finance

# Requirements
Python 3.7+ is needed. It has only been tested on Windows 10, but should in theory work on MacOS and linux environments.

The program relies on 5 Python Modules:
- PySimpleGUI
- aiohttp
- asyncio
- BeautifulSoup
- pytest

# Running the program
create a new python virtual environment and activate it.

install the requirements 

    $pip install -r requirements.txt

run the program

    $ python stock_price.py

A pop-up will appear with space to enter stock ticker symbols

# How it works
The interface is implemented as a desktop program, using the PySimpleGui package. When invoked, the program brings up a simple window with an input box for typing in a comma separated list of stock ticker symbols.

After the symbols are entered by the user, the program parses the individual symbols from the input string and creates URLs for each symbol.

Asynchronous calls are made to each URL, and the return HTML is saved.

The html strings are then parsed and the most recent stock price values are extracted. Once all stock prices are extracted for every ticker, a new pop-up window appears and the tickers and associated prices are displayed to the user.

Once the user closes the window with the stock prices displayed, they can choose to enter more ticker symbols or exit the program.

# Issues
A number of issues arose while creating this application.

## symbol validation
Very little ticker symbol validation is performed. If the user enters an invalid symbol, yahoo finance returns html without a \<table> element. When this happens, the pop-up window that displays the current prices will contain a list of invalid symbols.

Some tickers do return valid pages, but they may refer to out-of-date symbols, or other random issues. In this case, the symbol will appear in the list of valid symbols, but the prices will all be "n/a". One area of improvement would be to first validate the given symbol is indeed an active symbol on some stock exchange in the world.

A malicious user could enter in a very long string in the input box. No check is currently done to limit this.

If a request for current price is made to yahoo finance when the stock market is still open, yahoo finance does return a close price. This is potentially misleading to the user, as this implies the market has closed. An improvement would be to check the current time and see if the market is still open when the request was made. then the close column could be omitted entirely, or a "-" calue placed in the column to indicate the closing price has not been fixed yet.

if the request for price data is done before the market opens, the user is notified the prices will be from the previous open-day, and the date the price data is from is displayed in the corresponding window. However, the program determines if the market is opened based on stock markets based in the United States. If a user is interested in stock symbols found in different markets, the results will be confusing to them.

basically, dates and time and timezones are hard. Lots of little bugs related to this issue.

## Clunky User Interface
Separate windows are used for data entry, and data display. An area of improvement would be to create a single window that contains an input box and a display table.

## Networking issues
Currently, no checks are made to ensure a valid connection to the internet exists. In the case there is no internet connection, the program will crash.

Furthermore, the timeout for waiting for a response from yaho finance is left as default, which I believe is 5 minutes. This should be tightened up in a production environment. A status signal indicating the program is still working would improve user experience in the event of a slow connection. I tested this while connected to a hotspot from my cell phone, and the response took nearly 30 seconds.

## Inadequate automated testing
The automated testing suite currently only contains a single test case. Many more test cases are needed for a production quality application.

## Logging
The program "logs" with print statements. A proper logging mechanism should be used.

## Alternate Platforms
The program has been tested on a windows machine only. It should work on other platforms, but has not been teted.

# Architecture
The program is written in a basic layered style. the top layer consists of the GUI the user interacts with. The lower layer consists of the asynchronous calls to yahoo finance and associated html parsing.

An object oriented style is used to keep track of all data related to each stock ticker entered by the user. A stock ticker object contains a number of attributes:
- symbol: string value correlated to the symbol used by the stock exchange on which the ticker is listed.
- valid: boolean value indicating if the symbol is a valid symbol on some stock exchange
- open/high/low/close prices: the current daily price information for the ticker symbol. These are stored as strings since they come in as part of an html string and are displayed as strings by the UI.

A StockSymbol object has 2 methods:
- create_yf_url(): creates a valid yahoo finance url for checking the price of the corresponding stock symbol
- extract_from_html(): given a return html strong from yahoo finance, this method extracts the most recent price data.
