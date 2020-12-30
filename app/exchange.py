from json import dumps

from app.binance import Binance
from app.luno import Luno


class Exchange:
    def __init__(self):
        self.luno = Luno()
        self.luno.init_exchange()
        self.binance = Binance()
        self.binance.init_exchange()
    
    def get_binance_profit_taker_fee(self, quantity):
        binance_fee = self.binance.taker_fee * self.binance.sell_price
        luno_fee = self.luno.taker_fee * self.luno.buy_price
        return (binance_fee + luno_fee) * quantity

    def get_luno_profit_taker_fee(self, quantity):
        binance_fee = self.binance.taker_fee * self.binance.buy_price
        luno_fee = self.luno.taker_fee * self.luno.sell_price
        return (binance_fee + luno_fee) * quantity

    def take(self):
        can_profit_on_binance = self.binance.sell_price > self.luno.buy_price
        can_profit_on_luno = self.luno.sell_price > self.binance.buy_price
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
        print(f'can_profit_on_binance - {can_profit_on_binance}')
        print(f'can_profit_on_luno - {can_profit_on_luno}')
        if (can_profit_on_binance and can_profit_on_luno):
            print(f'luno stats - {dumps(self.luno.price_info(), indent=4)}')
            print(f'binance stats - {dumps(self.binance.price_info(), indent=4)}')

        if can_profit_on_binance:
            quantity = min(self.binance.sell_quantity, self.luno.buy_quantity) # perform a check here to confirm that we can afford this and then skip.... 
            # also create a job that routinely checks our balance and sends an email when our balance is less than a threshold. Create a mechanism for dynamically changing this value with an environment variable
            trade_fee = self.get_binance_profit_taker_fee(quantity)
            should_execute_trade = ((self.binance.sell_price - self.luno.buy_price) * quantity) > trade_fee
            print(f'\t\t BINANCE PROFIT: {(self.binance.sell_price - self.luno.buy_price) * quantity}')
            print(f'\t\t BINANCE PROFIT FEES: {trade_fee}')
            print(f'\t\t Will execute the trade: {should_execute_trade}')
            if should_execute_trade:
                # sell on binance
                print(f'Selling on Binance - quantity: {quantity} amount in Naira: {quantity * self.binance.sell_price}')
                self.binance.sell_as_taker(quantity)
                # buy on luno
                print(f'Buying on Luno - quantity: {quantity} amount in Naira: {quantity * self.luno.buy_price}')
                self.luno.buy_as_taker(quantity * self.luno.buy_price)
        if can_profit_on_luno:
            quantity = min(self.binance.buy_quantity, self.luno.sell_quantity) # perform a check here to confirm that we can afford this
            trade_fee = self.get_luno_profit_taker_fee(quantity)

            should_execute_trade = ((self.luno.sell_price - self.binance.buy_price) * quantity) > trade_fee
            print(f'\t\t LUNO PROFIT {(self.luno.sell_price - self.binance.buy_price) * quantity}')
            print(f'\t\t LUNO PROFIT FEES: {trade_fee}')
            print(f'\t\t Will execute the trade: {should_execute_trade}')
            if should_execute_trade:
                # sell on luno
                print(f'Selling on Luno - quantity: {quantity} amount in Naira: {quantity * self.luno.sell_price}')
                self.luno.sell_as_taker(quantity * self.luno.sell_price)
                # buy on binance
                print(f'Buying on Binance - quantity: {quantity} amount in Naira: {quantity * self.binance.buy_price}')
                self.binance.buy_as_taker(quantity)
