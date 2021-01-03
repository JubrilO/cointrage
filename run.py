from app.base_model import Base, engine
from app.market import Market
from app.exchange_list import ExchangeList

Base.metadata.create_all(engine)

if __name__ == "__main__":
    # luno = Luno()
    # luno.run()
    ExchangeList.init_exchange()
    market = Market()
    market.run()
