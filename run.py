from app.base_model import Base, engine
from app.market import Market

Base.metadata.create_all(engine)

if __name__ == "__main__":
    # luno = Luno()
    # luno.run()
    market = Market()
    market.run()
