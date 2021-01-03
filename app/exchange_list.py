import sqlalchemy as db
from .base_model import Base, session, engine
from sqlalchemy_utils import ArrowType
import arrow

class ExchangeList(Base):
    __tablename__ = 'exchange_list'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __init__(self, id, name):
        self.id = id
        self.name = name

    @staticmethod
    def get_one(name):
        return session.query(ExchangeList).filter_by(name=name).first()

    @staticmethod
    def init_exchange():
        LIST_OF_EXCHANGES = [
            {
                'id': 1,
                'name': 'luno',
            },
            {
                'id': 2,
                'name': 'binance',
            },
        ]
        for exchange in LIST_OF_EXCHANGES:
            if not ExchangeList.get_one(exchange['name']):
                item = ExchangeList(**exchange)
                session.add(item)
        session.commit()
    
    @staticmethod
    def get_items():
        return [exchange.to_dict() for exchange in session.query(ExchangeList).all()]
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }