import sys

from app.base_model import Base, engine
from app.market import Market

Base.metadata.create_all(engine)

if __name__ == "__main__":
    try:
        market = Market()
        market.run()
    except:
        print(f'An error occurred {sys.exc_info()}')
