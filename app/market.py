from pprint import pprint
from time import sleep

from app.binance import Binance
from app.luno import Luno
from app.utils import floater

class Market:
    def run(self):
        trading_amount = 5000 # since I dont know how to get this to be variable
        while True:
            binance = Binance()
            binance_ticker = binance.get_ticker()
            binance_sell_price = floater(binance_ticker['askPrice'])
            binance_profit_quantity = floater(binance_ticker['askQty'])
            binance_sell_volume = binance_sell_price * binance_profit_quantity
            print(f'binance_sell_price = {binance_sell_price}')
            binance_buy_price = floater(binance_ticker['bidPrice'])
            binance_buy_quantity = floater(binance_ticker['bidQty'])
            binance_buy_volume = binance_buy_price * binance_buy_quantity
            print(f'binance_buy_price = {binance_buy_price}')

            binance_taker_fee = binance.get_trade_fee()['tradeFee'][0]['taker'] * binance_sell_price # I'm not so sure what price will be used to determine the exchange for the trade fee. But I went with the more expensive one for now. Will investigate this later.
            # print(f'binance_taker_fee = {binance_taker_fee}')

            luno = Luno()
            luno_ticker = luno.get_ticker()
            print(luno_ticker)
            luno_sell_price = floater(luno_ticker['ask'])
            luno_buy_price = floater(luno_ticker['bid'])

            luno_taker_fee = floater(luno.get_trade_fee()['taker_fee']) * luno_sell_price
            print(f'luno_sell_price = {luno_sell_price}')
            print(f'luno_buy_price = {luno_buy_price}')

            selling_is_higher_on_binance = binance_sell_price > luno_sell_price
            buying_is_higher_on_binance = binance_buy_price > luno_buy_price

            binance_profit_quantity = trading_amount / binance_sell_price
            luno_profit_quantity = trading_amount / luno_sell_price
            can_make_a_profit = False
            if selling_is_higher_on_binance:
                can_make_a_profit = (binance_sell_price - luno_buy_price) > (binance_taker_fee + luno_taker_fee)
                if can_make_a_profit:
                    # This means that given the same crypto quantity e.g. 0.00043561326637550857, 
                    # we will sell 5k worth on binance and buy less than 5k (e.g. 4960) on Luno
                    # sell on binance
                    print(f'Selling on Binance - {binance_profit_quantity}')
                    # buy on luno
                    print(f'Buying on Luno - {binance_profit_quantity}')
                    pass
            else:
                can_make_a_profit = (luno_sell_price - binance_buy_price) > (binance_taker_fee + luno_taker_fee)
                if can_make_a_profit:
                    print(f'can make a profit selling on LUNO and buying on BINANCE {can_make_a_profit}')
                    # sell on luno
                    print(f'Selling on Luno - {luno_profit_quantity}')
                    # buy on binance
                    print(f'Buying on Binance - {luno_profit_quantity}')
                    pass
            sleep(5)
