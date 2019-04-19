from collections import OrderedDict
from util.printable import Printable

recipient_str = 'recipient'
sender_str = 'sender'
amount_str = 'amount'


class Transaction(Printable):

    def __init__(self, sender, recipient, signature, amount):
        # Constructor is parameterized and it is passing parameter to class object(transaction)
        self.sender = sender
        self.recipient = recipient
        self.signature = signature
        self.amount = amount

    def to_order_dict(self):
        # it is to create a ordered dict for hashing
        return OrderedDict([(sender_str, self.sender),
                            (recipient_str, self.recipient),
                            (amount_str, self.amount)])
