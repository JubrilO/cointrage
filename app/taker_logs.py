import sqlalchemy as db
from .base_model import Base, session, engine
from sqlalchemy_utils import ArrowType
import arrow

class TakerLogs(Base):
    __tablename__ = 'taker_logs'

    id = db.Column(db.Integer, primary_key=True)
    selling_exchange_id = db.Column(db.Integer)
    buying_exchange_id = db.Column(db.Integer)
    selling_price = db.Column(db.Float)
    buying_price = db.Column(db.Float)
    trade_quantity = db.Column(db.Float)
    profit_amount = db.Column(db.Float)
    trade_executed = db.Column(db.Boolean)
