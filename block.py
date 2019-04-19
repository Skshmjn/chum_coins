from time import time
from util.printable import Printable


class Block(Printable):
    def __init__(self, index, previous_hash, proof, transactions, timestamp=time()):

        # Constructor is parameterized and it is passing parameter to class object(block)
        self.index = index
        self.previous_hash = previous_hash
        self.proof = proof
        self.transactions = transactions

        self.timestamp = timestamp
