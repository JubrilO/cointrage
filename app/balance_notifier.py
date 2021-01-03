'''
This program periodically checks our balance and sends an email to the admin when the
account balance across the exchanges is below a predefined amount
'''

import os
from time import time

from dotenv import find_dotenv, load_dotenv
from redis import Redis

from app.binance import Binance
from app.luno import Luno
from app.utils import float_this, send_email

load_dotenv(find_dotenv())
BALANCE_THRESHOLD = float_this(os.getenv('BALANCE_THRESHOLD'))

redis = Redis()

class TradingBalanceChecker:

    def __init__(self):
        luno = Luno()
        binance = Binance()
        self.luno_balance = float_this(luno.get_available_naira_balance())
        self.binance_balance = float_this(binance.get_available_naira_balance())

    def run(self):
        balance_is_below_threshold = self.luno_balance < BALANCE_THRESHOLD or self.binance_balance < BALANCE_THRESHOLD
        if balance_is_below_threshold:
            email_sent_at = float_this(redis.get('email_sent_at'))
            print(f'email_sent_at - {email_sent_at}')
            if time() - email_sent_at > 3600 or email_sent_at == 0.0:
                # send an email once every hour
                print('sending email')
                return self.send_balance_exceeded_email()
    
    def send_balance_exceeded_email(self):
        body = f'''\
            Subject: [Cointrage] Your Cointrage Balance is Low
            \nYour LUNO Balance is: NGN{self.luno_balance}
            \nYour BINANCE Balance is: NGN{self.binance_balance}
            '''
        send_email(body)
        redis.set('email_sent_at', time())
