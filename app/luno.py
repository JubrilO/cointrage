from luno_python.client import Client
import sqlalchemy as db
from .base_model import Base, session, engine
from luno_python.client import Client
from pprint import pprint
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

API_KEY_ID = os.getenv('API_KEY_ID')
API_KEY_SECRET = os.getenv('API_KEY_SECRET')
ACCOUNT_NAME = os.getenv('ACCOUNT_NAME')

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
            resp = c.get_balances()
            if resp and resp.get('balance'):
                accounts = resp['balance']
                luno_accounts = [account for account in accounts if account and account.get('name') == account_name]
                self.cached_account = luno_accounts and luno_accounts[0]
        return self.cached_account

    def refresh_account(self, account_name):
        return self.get_account_via_balances(account_name)

    def sell_as_taker(self, amount):
        # if youre selling you have to quoate it in btc
        resp = c.post_market_order(pair='XBTNGN', type='SELL', base_account_id=self.account_id, base_volume=amount)
        # todo: store the order id in an order table
        return resp

    def buy_as_taker(self, amount):
        # if youre buying you have to quoate it in naira
        resp = c.post_market_order(pair='XBTNGN', type='BUY', counter_account_id=self.account_id, counter_volume=amount)
        # todo: store the order id in an order table
        return resp

    def get_order(self, order_id):
        return c.get_order(order_id)
    
    def get_ticker(self):
        return c.get_ticker('XBTNGN')

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
