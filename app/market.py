from pprint import pprint
from time import sleep

from app.binance import Binance
from app.luno import Luno
from app.utils import float_this

class Market:
    def run(self):
        while True:
            binance = Binance()
            binance_ticker = binance.get_ticker()

            binance_sell_price = float_this(binance_ticker['bidPrice'])
            binance_sell_quantity = float_this(binance_ticker['bidQty'])

            binance_buy_price = float_this(binance_ticker['askPrice'])
            binance_buy_quantity = float_this(binance_ticker['askQty'])

            binance_taker_fee = binance.get_trade_fee()['tradeFee'][0]['taker'] * binance_sell_price # I'm not so sure what price will be used to determine the exchange for the trade fee. But I went with the more expensive one for now. Will investigate this later.

            luno = Luno()
            # luno_ticker = luno.get_ticker() # implement get ticker to get the first ask and bids instead of calling luno.get_order_book directly
            luno_order_book = luno.get_order_book()
            luno_ask = luno_order_book['asks'][0]
            luno_bid = luno_order_book['bids'][0]

            luno_buy_price = float_this(luno_ask['price'])
            luno_buy_quantity = float_this(luno_ask['volume'])

            luno_sell_price = float_this(luno_bid['price'])
            luno_sell_quantity = float_this(luno_bid['volume'])

            luno_taker_fee = float_this(luno.get_trade_fee()['taker_fee']) * luno_sell_price

            binance_profit = binance_sell_price > luno_buy_price
            luno_profit = luno_sell_price > binance_buy_price
            '''
            We might not be able to make a profit in the scenario below
            - binance
                - BUY:  12.7 million naira
                - SELL: 12.4 million naira
            - luno
                - BUY:  12.8 million naira
                - SELL: 12.6 million naira
            '''
            print('\n\n')
            print(f'binance_profit - {binance_profit}')
            print(f'luno_profit - {luno_profit}')

            if binance_profit:
                quantity = min(binance_sell_quantity, luno_buy_quantity) # perform a check here to confirm that we can afford this and then skip.... 
                # also create a job that routinely checks our balance and sends an email when our balance is less than a threshold. Create a mechanism for dynamically changing this value with an environment variable
                should_execute_trade = (binance_sell_price * quantity - luno_buy_price * quantity) > (binance_taker_fee * quantity + luno_taker_fee * quantity)
                print(f'\t\t BINANCE PROFIT: {binance_sell_price * quantity - luno_buy_price * quantity}')
                print(f'\t\t BINANCE PROFIT FEES: {binance_taker_fee * quantity + luno_taker_fee * quantity}')
                print(f'\t\t Will execute the trade: {should_execute_trade}')
                if should_execute_trade:
                    # sell on binance
                    print(f'Selling on Binance - quantity: {quantity} amount in Naira: {quantity * binance_sell_price}')
                    binance.sell_as_taker(quantity)
                    # buy on luno
                    print(f'Buying on Luno - quantity: {quantity} amount in Naira: {quantity * luno_buy_price}')
                    luno.sell_as_taker(quantity * luno_buy_price)
            if luno_profit:
                quantity = min(binance_buy_quantity, luno_sell_quantity) # perform a check here to confirm that we can afford this
                should_execute_trade = (luno_sell_price * quantity - binance_buy_price * quantity) > (binance_taker_fee * quantity + luno_taker_fee * quantity)
                print(f'\t\t LUNO PROFIT {luno_sell_price * quantity - binance_buy_price * quantity}')
                print(f'\t\t LUNO PROFIT FEES: {binance_taker_fee * quantity + luno_taker_fee * quantity}')
                print(f'\t\t Will execute the trade: {should_execute_trade}')
                if should_execute_trade:
                    # sell on luno
                    print(f'Selling on Luno - quantity: {quantity} amount in Naira: {quantity * luno_sell_price}')
                    luno.sell_as_taker(quantity * luno_sell_price)
                    # buy on binance
                    print(f'Buying on Binance - quantity: {quantity} amount in Naira: {quantity * binance_buy_price}')
                    binance.buy_as_taker(quantity)
            sleep(1)


# todo:
# - create a PR for what we have now that has the actual buy and sell logic
# - implement an exchange class that abstracts most of the variable names here. See: https://github.com/JubrilO/cointrage/pull/3#discussion_r549094746
# - create a background job that checks our balance and then sends an email when our balance is less than a threshold. Create a mechanism for dynamically changing this value with an environment variable
# - add database logs for all the trading information.
# - modify the while loop to try and trade for 1 minute and create a job that runs the while loop every 2 minutes
