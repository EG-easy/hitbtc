import uuid
import logging
import requests
from decimal import *
from time import time, sleep

UPPER_PRICE = 0.060
LOWER_PRICE = 0.057
LIMIT = -0.001
AMOUNT = 0.001
CURRENCY_PAIR = 'ETHBTC'
public_key = "xxx"  # API Key
secret = "xxx"  # Secret Key

# setting log
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)

class Client(object):
    def __init__(self, url, public_key, secret):
        self.url = url + "/api/2"
        self.session = requests.session()
        self.session.auth = (public_key, secret)

    def get_ticker(self, symbol_code):
        """Get ticker."""
        return self.session.get("%s/public/ticker/%s" % (self.url, symbol_code)).json()

    def get_symbol(self, symbol_code):
        """Get symbol."""
        return self.session.get("%s/public/symbol/%s" % (self.url, symbol_code)).json()

    def get_orderbook(self, symbol_code):
        """Get orderbook. """
        return self.session.get("%s/public/orderbook/%s" % (self.url, symbol_code)).json()

    def get_trading_balance(self):
        """Get trading balance."""
        return self.session.get("%s/trading/balance" % self.url).json()

    def new_order(self, client_order_id, symbol_code, side, quantity, price=None):
        """Place an order."""
        data = {'symbol': symbol_code, 'side': side, 'quantity': quantity}

        if price is not None:
            data['price'] = price

        return self.session.put("%s/order/%s" % (self.url, client_order_id), data=data).json()


if __name__ == "__main__":

    client = Client("https://api.hitbtc.com", public_key, secret)

    # get eth trading balance
    eth_balance = 0.0
    balances = client.get_trading_balance()
    for balance in balances:
        if balance['currency'] == 'ETH':
            eth_balance = float(balance['available'])

    print('Current ETH balance: %s' % eth_balance)

    orderbook = client.get_orderbook('ETHBTC')
    eth_btc = client.get_symbol('ETHBTC')
    # sell order price
    best_price = Decimal(orderbook['bid'][0]['price']) + Decimal(eth_btc['tickSize'])
    # buy order price
    limit_price = Decimal(best_price) + Decimal(LIMIT)
    # current price
    ticker = client.get_ticker('ETHBTC')
    last_price = Decimal(ticker['last'])

    # initialize counter
    counter = 1

    while Decimal(last_price) < UPPER_PRICE and Decimal(last_price) > LOWER_PRICE and counter <= 3:
        logger.info('ラウンド{}開始'.format(counter))
        logger.info('現在価格: {}'.format(last_price))

        client_order_id = uuid.uuid4().hex
        order = client.new_order(client_order_id, 'ETHBTC', 'sell', AMOUNT, best_price)
        if 'error' not in order:
            logger.info('売り注文価格: {}'.format(best_price))
        else:
            print(order['error'])

        client_order_id = uuid.uuid4().hex
        order = client.new_order(client_order_id, 'ETHBTC', 'buy', AMOUNT,limit_price)
        if 'error' not in order:
            logger.info('買い注文価格: {}'.format(limit_price))
        else:
            print(order['error'])

        logger.info('ラウンド{}終了'.format(counter))
        logger.info('30秒後に次ラウンド開始\n')
        sleep(30)
        counter += 1

    else:
        print("end")