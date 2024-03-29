import sqlalchemy as db
from .base_model import Base, session, engine
from binance.client import Client
from pprint import pprint
import os
from dotenv import load_dotenv, find_dotenv
from app.utils import float_this

load_dotenv(find_dotenv())

API_KEY_ID = os.getenv('BINANCE_API_KEY')
API_KEY_SECRET = os.getenv('BINANCE_SECRET_KEY')
ACCOUNT_NAME = os.getenv('ACCOUNT_NAME')
ENVIRONMENT = os.getenv('ENVIRONMENT')

c = Client(API_KEY_ID, API_KEY_SECRET)

class Binance(Base):
    __tablename__ = 'binance'

    cached_ngn_account = {} # temporary cache
    cached_btc_account = {} # temporary cache

    id = db.Column(db.Integer, primary_key=True)
    ngn_balance = db.Column(db.String, default='0.0')
    btc_balance = db.Column(db.String, default='0.0')
    ngn_locked = db.Column(db.String, default='0.0')
    btc_locked = db.Column(db.String, default='0.0')

    def get_account(self):
        self.cached_ngn_account = {}
        self.cached_btc_account = {}
        if not (self.cached_ngn_account or self.cached_btc_account):
            resp = c.get_account()
            if resp and resp.get('balances'):
                balances = resp['balances']
                binance_accounts = [balance for balance in balances if balance and balance.get('asset') in ['NGN', 'BTC']]
                ngn_balance = [balance for balance in binance_accounts if balance.get('asset') == 'NGN']
                btc_balance = [balance for balance in binance_accounts if balance.get('asset') == 'BTC']
                
                self.cached_ngn_account = ngn_balance[0]
                self.cached_btc_account = btc_balance[0]
                account = Binance(
                    ngn_balance=self.cached_ngn_account['free'],
                    btc_balance=self.cached_btc_account['free'],
                    ngn_locked=self.cached_ngn_account['locked'],
                    btc_locked=self.cached_btc_account['locked'],
                )
                session.add(account)
                session.commit()
        return {
            'available_naira_balance': self.cached_ngn_account['free'],
            'locked_naira_balance': self.cached_ngn_account['locked'],
            'available_btc_balance': self.cached_btc_account['free'],
            'locked_btc_balance': self.cached_btc_account['locked'],
        }
    
    def get_available_naira_balance(self):
        return self.refresh_account()['available_naira_balance']

    def refresh_account(self):
        return self.get_account()

    def sell_as_taker(self, price, quantity):
        del price
        if ENVIRONMENT != 'production':
            return
        resp = c.order_market_sell(
            symbol='BTCNGN',
            quantity=quantity)
        return resp

    def buy_as_taker(self, price, quantity):
        del price
        if ENVIRONMENT != 'production':
            return
        resp = c.order_market_buy(
            symbol='BTCNGN',
            quantity=quantity)
        return resp

    def get_avg_price(self):
        return c.get_avg_price(symbol='BTCNGN')
    
    def get_ticker(self):
        return c.get_ticker(symbol='BTCNGN')
    
    def get_trade_fee(self):
        return c.get_trade_fee(symbol='BTCNGN')
    
    def to_dict(self):
        return {
            'id': self.id,
            'ngn_balance': self.ngn_balance,
            'btc_balance': self.btc_balance,
            'ngn_locked': self.ngn_locked,
            'btc_locked': self.btc_locked,
        }

    def run(self):
        self.get_account()

    def init_exchange(self):
        self.name = self.__tablename__

        self.ticker = self.get_ticker()

        self.sell_price = float_this(self.ticker['bidPrice'])
        self.sell_quantity = float_this(self.ticker['bidQty'])

        self.buy_price = float_this(self.ticker['askPrice'])
        self.buy_quantity = float_this(self.ticker['askQty'])

        taker_fee = c._request_withdraw_api('get', 'tradeFee.html', True, data={'symbol': 'BTCNGN'})
        if not taker_fee.get('success'):
            res = {
                'tradeFee': [{'taker': '0.001'}],
            }
        else:
            res = taker_fee
        self.taker_fee = float_this(res['tradeFee'][0].get('taker')) # implement a function in the banance exchange class that protects us if the wrong data format is returned from binance. Do same for Luno

    def price_info(self):
        return {
            'exchange': self.__tablename__,
            'sell_price': self.sell_price,
            'sell_quantity': self.sell_quantity,
            'buy_price': self.buy_price,
            'buy_quantity': self.buy_quantity,
        }