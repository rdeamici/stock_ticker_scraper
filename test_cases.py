from stock_price import StockSymbol
from datetime import datetime, timedelta


class TestStockSymbol:
    symbol = StockSymbol('ISRG')
    cur_date = datetime.today()
    prev_date = cur_date - timedelta(days=1)

    def test_StockSymbol_url(self):
        self.symbol.create_yf_url(self.cur_date, self.prev_date)

        cur = int(self.cur_date.timestamp())
        pre = int(self.prev_date.timestamp())
        assert self.symbol.yf_url==f'https://finance.yahoo.com/quote/ISRG/history?period1={pre}&period2={cur}&interval=1d'
        