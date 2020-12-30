from app.luno import Luno
from app.binance import Binance

class Exchange:
    def __init__(self):
        self.luno = Luno()
        self.luno.init_exchange()
        self.binance = Binance()
        self.binance.init_exchange()
