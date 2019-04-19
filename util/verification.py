from util.hash_util import hash_block, hashing
from wallet import Wallet


class Verification:

    # proof of work logic
    # generally use to limit blockchain for adding so many blocks in less amount of time
    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        # encode For efficient storage of these strings
        guess = (str([tx.to_order_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
        guess_hash = hashing(guess)
        # proof of work problem
        return guess_hash[0:2] == '00'

    # verify chain not transactions
    @classmethod
    def verify_chain(cls, blockchain):
        for (index, block) in enumerate(blockchain):
            # for genesis block
            if index == 0:
                # skipping for genesis block as genesis block doesn't have previous block
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                # checking previous_hash in current block with hashing previous block
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                # checking whether blockchain have proper valid proof or not and -1 is for removing mining block
                return False
        return True

    # verify single transaction
    @staticmethod
    def verify_transaction(transactions, get_balance, money_check=True):
        if money_check:
            sender_balance = get_balance(transactions.sender)
            return sender_balance >= transactions.amount and Wallet.verify_transaction(transactions)
        else:
            return Wallet.verify_transaction(transactions)

    # verify all transaction
    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        return all([cls.verify_transaction(tx, get_balance, False) for tx in open_transactions])
