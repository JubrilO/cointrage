from app.balance_notifier import TradingBalanceChecker
from app.base_model import Base, engine

Base.metadata.create_all(engine)

if __name__ == "__main__":
    checker = TradingBalanceChecker()
    checker.run()
