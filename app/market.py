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
            exchange.take()
            sleep(1)


# todo:
# - create a PR for what we have now that has the actual buy and sell logic
# - implement an exchange class that abstracts most of the variable names here. See: https://github.com/JubrilO/cointrage/pull/3#discussion_r549094746
# - create a background job that checks our balance and then sends an email when our balance is less than a threshold. Create a mechanism for dynamically changing this value with an environment variable
# - add database logs for all the trading information.
# - modify the while loop to try and trade for 1 minute and create a job that runs the while loop every 2 minutes
