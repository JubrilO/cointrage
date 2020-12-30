from pprint import pprint
from time import sleep

# from app.binance import Binance
# from app.luno import Luno
from app.exchange import Exchange
from app.utils import float_this

class Market:
    def run(self):
        while True:
            exchange = Exchange()

            exchange.binance.profit = exchange.binance.sell_price > exchange.luno.buy_price
            exchange.luno.profit = exchange.luno.sell_price > exchange.binance.buy_price
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
            print(f'exchange.binance.profit - {exchange.binance.profit}')
            print(f'exchange.luno.profit - {exchange.luno.profit}')

            if exchange.binance.profit:
                quantity = min(exchange.binance.sell_quantity, exchange.luno.buy_quantity) # perform a check here to confirm that we can afford this and then skip.... 
                # also create a job that routinely checks our balance and sends an email when our balance is less than a threshold. Create a mechanism for dynamically changing this value with an environment variable
                exchange.binance.fee = exchange.binance.taker_fee * exchange.binance.sell_price
                exchange.luno.fee = exchange.luno.taker_fee * exchange.luno.buy_price
                total_fees = (exchange.binance.fee + exchange.luno.fee) * quantity
                should_execute_trade = (exchange.binance.sell_price * quantity - exchange.luno.buy_price * quantity) > total_fees
                print(f'\t\t BINANCE PROFIT: {exchange.binance.sell_price * quantity - exchange.luno.buy_price * quantity}')
                print(f'\t\t BINANCE PROFIT FEES: {total_fees}')
                print(f'\t\t Will execute the trade: {should_execute_trade}')
                if should_execute_trade:
                    # sell on binance
                    print(f'Selling on Binance - quantity: {quantity} amount in Naira: {quantity * exchange.binance.sell_price}')
                    # exchange.binance.sell_as_taker(quantity)
                    # buy on luno
                    print(f'Buying on Luno - quantity: {quantity} amount in Naira: {quantity * exchange.luno.buy_price}')
                    # exchange.luno.buy_as_taker(quantity * exchange.luno.buy_price)
            if exchange.luno.profit:
                quantity = min(exchange.binance.buy_quantity, exchange.luno.sell_quantity) # perform a check here to confirm that we can afford this
                exchange.binance.fee = exchange.binance.taker_fee * exchange.binance.buy_price
                exchange.luno.fee = exchange.luno.taker_fee * exchange.luno.sell_price
                total_fees = (exchange.binance.fee + exchange.luno.fee) * quantity
                should_execute_trade = (exchange.luno.sell_price * quantity - exchange.binance.buy_price * quantity) > total_fees
                print(f'\t\t LUNO PROFIT {exchange.luno.sell_price * quantity - exchange.binance.buy_price * quantity}')
                print(f'\t\t LUNO PROFIT FEES: {total_fees}')
                print(f'\t\t Will execute the trade: {should_execute_trade}')
                if should_execute_trade:
                    # sell on luno
                    print(f'Selling on Luno - quantity: {quantity} amount in Naira: {quantity * exchange.luno.sell_price}')
                    # exchange.luno.sell_as_taker(quantity * exchange.luno.sell_price)
                    # buy on binance
                    print(f'Buying on Binance - quantity: {quantity} amount in Naira: {quantity * exchange.binance.buy_price}')
                    # exchange.binance.buy_as_taker(quantity)
            sleep(1)


# todo:
# - create a PR for what we have now that has the actual buy and sell logic
# - implement an exchange class that abstracts most of the variable names here. See: https://github.com/JubrilO/cointrage/pull/3#discussion_r549094746
# - create a background job that checks our balance and then sends an email when our balance is less than a threshold. Create a mechanism for dynamically changing this value with an environment variable
# - add database logs for all the trading information.
# - modify the while loop to try and trade for 1 minute and create a job that runs the while loop every 2 minutes
