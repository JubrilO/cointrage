import sqlalchemy as db
from .base_model import Base, session, engine
from binance.client import Client
from pprint import pprint
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

API_KEY_ID = os.getenv('BINANCE_API_KEY')
API_KEY_SECRET = os.getenv('BINANCE_SECRET_KEY')
ACCOUNT_NAME = os.getenv('ACCOUNT_NAME')

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
        account = session.query(Binance).filter(Binance.name == ACCOUNT_NAME).first()
        if not account:
            data = self.get_account_from_binance()

    def get_account_from_binance(self):
        self.cached_ngn_account = {}
        self.cached_btc_account = {}
        if not (self.cached_ngn_account or self.cached_btc_account):
            resp = c.get_account()
            if resp and resp.get('balances'):
                balances = resp['balances']
                binance_accounts = [balance for balance in balances if balance and balance.get('asset') in ['NGN', 'BTC']]
                pprint(binance_accounts)
                ngn_balance = [balance for balance in binance_accounts if balance.get('asset') == 'NGN']
                btc_balance = [balance for balance in binance_accounts if balance.get('asset') == 'BTC']
                
                self.cached_ngn_account = ngn_balance[0]
                self.cached_btc_account = btc_balance[0]
        # return self.cached_account

    def refresh_account(self):
        return self.get_account_from_binance()

    def sell_as_taker(self, quantity):
        resp = c.order_market_sell(
            symbol='BTCNGN',
            quantity=quantity)
        return resp

    def buy_as_taker(self, quantity):
        resp = c.order_market_buy(
            symbol='BTCNGN',
            quantity=quantity)
        return resp

    # def get_order(self, order_id):
    #     return c.get_order(order_id)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ngn_balance': self.ngn_balance,
            'btc_balance': self.btc_balance,
            'ngn_locked': self.ngn_locked,
            'btc_locked': self.btc_locked,
        }

    def run(self):
        binance_account = self.get_account()
        # pprint(self.buy_as_taker(0.1))
