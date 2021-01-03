from json import dumps

from app.binance import Binance
from app.luno import Luno


class Exchange:
    def __init__(self):
        self.luno = Luno()
        self.luno.init_exchange()
        self.binance = Binance()
        self.binance.init_exchange()
        self.can_profit_on_binance = self.binance.sell_price > self.luno.buy_price
        self.can_profit_on_luno = self.luno.sell_price > self.binance.buy_price
        self.can_profit = self.can_profit_on_binance or self.can_profit_on_luno

        '''
        We might not be able to make a profit in the scenario below
        - binance
            - BUY:  12.7 million naira
            - SELL: 12.4 million naira
        - luno
            - BUY:  12.8 million naira
            - SELL: 12.6 million naira
        '''

        if self.can_profit_on_binance:
            self.sell_exchange = self.binance
            self.buy_exchange = self.luno
    
        if self.can_profit_on_luno:
            self.sell_exchange = self.luno
            self.buy_exchange = self.binance
    
    def get_trade_fee(self, quantity):
        seller_fee = self.sell_exchange.taker_fee * self.sell_exchange.sell_price
        buyer_fee = self.buy_exchange.taker_fee * self.buy_exchange.buy_price
        return (seller_fee + buyer_fee) * quantity

    def take(self):
        print('\n\n')
        print(f'can_profit_on_binance - {self.can_profit_on_binance}')
        print(f'can_profit_on_luno - {self.can_profit_on_luno}')
        if (self.can_profit_on_binance and self.can_profit_on_luno):
            print(f'luno stats - {dumps(self.luno.price_info(), indent=4)}')
            print(f'binance stats - {dumps(self.binance.price_info(), indent=4)}')
            return

        if self.can_profit:
            quantity = min(self.sell_exchange.sell_quantity, self.buy_exchange.buy_quantity) # perform a check here to confirm that we can afford this and then skip.... 
            # also create a job that routinely checks our balance and sends an email when our balance is less than a threshold. Create a mechanism for dynamically changing this value with an environment variable
            trade_fee = self.get_trade_fee(quantity)
            profit = (self.sell_exchange.sell_price - self.buy_exchange.buy_price) * quantity
            should_execute_trade = (profit) > trade_fee
            print(f'\t\t {self.sell_exchange.name.upper()} PROFIT: {profit}')
            print(f'\t\t {self.sell_exchange.name.upper()} TRADE FEES: {trade_fee}')
            print(f'\t\t COINTRAGE PROFIT AFTER TRADING: {profit - trade_fee}')
            print(f'\t\t Will execute the trade: {should_execute_trade}')
            if should_execute_trade:
                # sell on binance
                print(f'Selling on {self.sell_exchange.name.title()} - quantity: {quantity} amount in Naira: {quantity * self.sell_exchange.sell_price}')
                self.sell_exchange.sell_as_taker(self.sell_exchange.sell_price, quantity)
                # buy on luno
                print(f'Buying on {self.buy_exchange.name.title()} - quantity: {quantity} amount in Naira: {quantity * self.buy_exchange.buy_price}')
                self.buy_exchange.buy_as_taker(self.buy_exchange.buy_price, quantity)
