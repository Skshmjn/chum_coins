import hashlib
import json

transactions_str = 'transactions'


def hashing(string):
    # returning hashing for various purpose
    return hashlib.sha256(string).hexdigest()


def hash_block(block):
    hashable_block = block.__dict__.copy()
    hashable_block[transactions_str] = [tx.to_order_dict() for tx in hashable_block[transactions_str]]
    d = hashlib.sha256(json.dumps(hashable_block, sort_keys=True).encode())
    # to sort attribute so that
    # it wont generate another hash
    d2 = hashlib.sha256()

    d2.update(d.digest())

    return d2.hexdigest()
