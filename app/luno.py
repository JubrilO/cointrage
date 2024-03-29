from luno_python.client import Client
import sqlalchemy as db
from .base_model import Base, session, engine
from luno_python.client import Client
from pprint import pprint
import os
from dotenv import load_dotenv, find_dotenv
from app.utils import float_this

load_dotenv(find_dotenv())

API_KEY_ID = os.getenv('API_KEY_ID')
API_KEY_SECRET = os.getenv('API_KEY_SECRET')
ACCOUNT_NAME = os.getenv('ACCOUNT_NAME')
ENVIRONMENT = os.getenv('ENVIRONMENT')

c = Client(api_key_id=API_KEY_ID, api_key_secret=API_KEY_SECRET)

class Luno(Base):
    __tablename__ = 'luno'

    cached_account = {} # temporary cache

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer)
    name = db.Column(db.String)
    currency = db.Column(db.String)
    balance = db.Column(db.Float, default=0.0)
    reserved = db.Column(db.Float, default=0.0)
    unconfirmed = db.Column(db.Float, default=0.0)

    def get_account(self):
        account = session.query(Luno).filter(Luno.name == ACCOUNT_NAME).first()
        if not account:
            data = self.get_account_via_balances(ACCOUNT_NAME)
            if data:
                account = Luno(
                    account_id=data['account_id'],
                    name=data['name'],
                    currency=data['asset'],
                    balance=data['balance'],
                    reserved=data['reserved'],
                    unconfirmed=data['unconfirmed'],
                )
                session.add(account)
                session.commit()
                return account
            print('Creating your account')
            data = self.create_account()
            account = Luno(
                account_id=data['id'],
                name=data['name'],
                currency=data['currency'],
            )
            session.add(account)
            session.commit()
            return account
        else:
            print('Account found')
            refreshed_account = self.refresh_account(ACCOUNT_NAME)
            account.balance = refreshed_account['balance']
            account.reserved = refreshed_account['reserved']
            account.unconfirmed = refreshed_account['unconfirmed']
            session.add(account)
            session.commit()
        return account

    def create_account(self):
        resp = c.create_account('XBT', ACCOUNT_NAME)
        return resp

    def get_account_via_balances(self, account_name):
        self.cached_account = {}
        if not self.cached_account:
            accounts = self.get_all_accounts()
            luno_accounts = [account for account in accounts if account and account.get('name') == account_name]
            self.cached_account = luno_accounts and luno_accounts[0]
        return self.cached_account

    def refresh_account(self, account_name):
        return self.get_account_via_balances(account_name)

    def get_available_naira_balance(self):
        accounts = self.get_all_accounts()
        naira_account = [account for account in accounts if account and account.get('asset') == 'NGN']
        if len(naira_account):
            return naira_account[0]['balance']
        return 0.0

    def get_all_accounts(self):
        resp = c.get_balances()
        if resp and resp.get('balance'):
            return resp['balance']
        return []        

    def sell_as_taker(self, price, quantity):
        if ENVIRONMENT != 'production':
            return
        del price
        # if youre selling you have to quote it in btc
        resp = c.post_market_order(pair='XBTNGN', type='SELL', base_account_id=self.account_id, base_volume=quantity)
        # todo: store the order id in an order table
        return resp

    def buy_as_taker(self, price, quantity):
        if ENVIRONMENT != 'production':
            return
        volume = price * quantity
        # if youre buying you have to quote it in naira
        resp = c.post_market_order(pair='XBTNGN', type='BUY', counter_account_id=self.account_id, counter_volume=volume)
        # todo: store the order id in an order table
        return resp

    def get_order(self, order_id):
        return c.get_order(order_id)
    
    def get_ticker(self):
        order_book = c.get_order_book('XBTNGN')
        return {
            'ask': order_book['asks'][0],
            'bid': order_book['bids'][0],
        }

    def get_trade_fee(self):
        return c.get_fee_info('XBTNGN')

    def get_order_book(self):
        return c.get_order_book('XBTNGN')

    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'name': self.name,
            'currency': self.currency,
            'balance': self.balance,
            'reserved': self.reserved,
            'unconfirmed': self.unconfirmed,
        }

    def run(self):
        luno_account = self.get_account()
        print(luno_account.get_ticker())

    def init_exchange(self):
        self.name = self.__tablename__
        self.ticker = self.get_ticker()

        self.sell_price = float_this(self.ticker['ask']['price'])
        self.sell_quantity = float_this(self.ticker['ask']['volume'])

        self.buy_price = float_this(self.ticker['bid']['price'])
        self.buy_quantity = float_this(self.ticker['bid']['volume'])

        self.taker_fee = float_this(self.get_trade_fee().get('taker_fee'))

    def price_info(self):
        return {
            'exchange': self.__tablename__,
            'sell_price': self.sell_price,
            'sell_quantity': self.sell_quantity,
            'buy_price': self.buy_price,
            'buy_quantity': self.buy_quantity,
        }