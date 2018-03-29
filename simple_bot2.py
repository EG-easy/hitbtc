import uuid
import logging
import requests
from decimal import *
from time import time, sleep

basis_price = 0.0552
LIMIT = [0.015, 0.03, 0.05]
POINT = [0.01, 0.02, 0.03]
AMOUNT = [0.001, 0.005, 0.02]
CURRENCY_PAIR = 'ETHBTC'
public_key = "???"  # Key
secret = "???"  # Secret

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

    # current price
    ticker = client.get_ticker('ETHBTC')
    last_price = Decimal(ticker['last'])

    # initialize counter
    counter = 1

    while counter <= 100:

        logger.info('round{} start'.format(counter))
        logger.info('current price: {}'.format(last_price))

        best_sell_price = Decimal(orderbook['bid'][0]['price']) + Decimal(eth_btc['tickSize'])
        best_buy_price = Decimal(orderbook['ask'][0]['price']) - Decimal(eth_btc['tickSize'])

        if Decimal(last_price) <= basis_price * (1 + LIMIT[0]) and Decimal(last_price) >= basis_price:
            logger.info('1st stage sell')
            client_order_id = uuid.uuid4().hex
            order = client.new_order(client_order_id, 'ETHBTC', 'sell', AMOUNT[0], best_sell_price)
            if 'error' not in order:
                logger.info('sell order price: {}'.format(best_sell_price))

                limit_price = basis_price * (1 - LIMIT[0])
                client_order_id = uuid.uuid4().hex
                order = client.new_order(client_order_id, 'ETHBTC', 'buy', AMOUNT[0], limit_price)
                if 'error' not in order:
                    logger.info('buy order price: {}'.format(limit_price))
                else:
                    print(order['error'])

            else:
                print(order['error'])

        elif Decimal(last_price) <= basis_price * (1 + LIMIT[1]) and Decimal(last_price) > basis_price* (1 + LIMIT[0]):
            logger.info('2nd stage sell')
            client_order_id = uuid.uuid4().hex
            order = client.new_order(client_order_id, 'ETHBTC', 'sell', AMOUNT[1], best_sell_price)
            if 'error' not in order:
                logger.info('sell order price: {}'.format(best_sell_price))
                limit_price = basis_price * (1 - LIMIT[1])
                client_order_id = uuid.uuid4().hex
                order = client.new_order(client_order_id, 'ETHBTC', 'buy', AMOUNT[1], limit_price)
                if 'error' not in order:
                    logger.info('buy order price: {}'.format(limit_price))
                else:
                    print(order['error'])
            else:
                print(order['error'])

        elif Decimal(last_price) <= basis_price * (1 + LIMIT[2]) and Decimal(last_price) > basis_price* (1 + LIMIT[1]):
            logger.info('3rd stage sell')
            client_order_id = uuid.uuid4().hex
            order = client.new_order(client_order_id, 'ETHBTC', 'sell', AMOUNT[2], best_sell_price)
            if 'error' not in order:
                logger.info('sell order price: {}'.format(best_sell_price))
                limit_price = basis_price * (1 - LIMIT[2])
                client_order_id = uuid.uuid4().hex
                order = client.new_order(client_order_id, 'ETHBTC', 'buy', AMOUNT[2], limit_price)
                if 'error' not in order:
                    logger.info('buy order price: {}'.format(limit_price))
                else:
                    print(order['error'])
            else:
                print(order['error'])

        elif Decimal(last_price) >= basis_price * (1 - LIMIT[0]) and Decimal(last_price) < basis_price:
            logger.info('1st stage buy')
            client_order_id = uuid.uuid4().hex
            order = client.new_order(client_order_id, 'ETHBTC', 'buy', AMOUNT[0], best_buy_price)
            if 'error' not in order:
                logger.info('buy order price: {}'.format(best_buy_price))

                limit_price = basis_price * (1 + LIMIT[0])
                client_order_id = uuid.uuid4().hex
                order = client.new_order(client_order_id, 'ETHBTC', 'sell', AMOUNT[0], limit_price)
                if 'error' not in order:
                    logger.info('sell order price: {}'.format(limit_price))
                else:
                    print(order['error'])
            else:
                print(order['error'])

        elif Decimal(last_price) >= basis_price * (1 - LIMIT[1]) and Decimal(last_price) < basis_price* (1 - LIMIT[0]):
            logger.info('2nd stage buy')
            client_order_id = uuid.uuid4().hex
            order = client.new_order(client_order_id, 'ETHBTC', 'buy', AMOUNT[1], best_buy_price)
            if 'error' not in order:
                logger.info('buy order price: {}'.format(best_buy_price))

                limit_price = basis_price * (1 + LIMIT[1])
                client_order_id = uuid.uuid4().hex
                order = client.new_order(client_order_id, 'ETHBTC', 'sell', AMOUNT[1], limit_price)
                if 'error' not in order:
                    logger.info('sell order price: {}'.format(limit_price))
                else:
                    print(order['error'])

            else:
                print(order['error'])

        elif Decimal(last_price) >= basis_price * (1 - LIMIT[2]) and Decimal(last_price) < basis_price * (1 - LIMIT[1]):
            logger.info('3rd stage buy')
            client_order_id = uuid.uuid4().hex
            order = client.new_order(client_order_id, 'ETHBTC', 'buy', AMOUNT[2], best_buy_price)
            if 'error' not in order:
                logger.info('buy order price: {}'.format(best_buy_price))

                limit_price = basis_price * (1 + LIMIT[2])
                client_order_id = uuid.uuid4().hex
                order = client.new_order(client_order_id, 'ETHBTC', 'sell', AMOUNT[2], limit_price)
                if 'error' not in order:
                    logger.info('sell order price: {}'.format(limit_price))
                else:
                    print(order['error'])

            else:
                print(order['error'])

        else:
            counter +=100

        logger.info('round{} finish'.format(counter))
        logger.info('30 second later, start next round\n')
        sleep(30)
        counter += 1

    else:
        print("end")
