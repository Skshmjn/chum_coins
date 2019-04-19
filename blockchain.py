import json
import requests
from _functools import reduce

from util.hash_util import hash_block
from block import Block
from transaction import Transaction
from util.verification import Verification
from wallet import Wallet

Mining_reward = 1

index_str = 'index'
previous_hash_str = 'previous_hash'
proof_str = 'proof'
transactions_str = 'transactions'
recipient_str = 'recipient'
sender_str = 'sender'
amount_str = 'amount'
timestamp_str = 'timestamp'
signature_str = 'signature'


class Blockchain:
    def __init__(self, public_key, node_id):
        genesis_block = Block(0, '', 100, [], 0)
        # initialisation blockchain
        self.chain = [genesis_block]
        self.__open_transactions = []
        self.resolve_conflict = False

        self.public_key = public_key
        self.__peer_node = set()
        self.node_id = node_id
        self.load_data()

    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        self.__chain = val

    def get_open_transaction(self):
        return self.__open_transactions[:]

    # function to load data from file
    def load_data(self):

        try:
            with open('blockchain-{}.dat'.format(self.node_id), mode='r') as f:
                file_content = f.readlines()
                blockchain = json.loads(file_content[0][:-1])  # for rejecting \n from the save file
                updated_blockchain = []
                # converting json saved file into block and transaction objects
                for block in blockchain:
                    converted_tx = [Transaction(tx[sender_str], tx[recipient_str], tx[signature_str], tx[amount_str])
                                    for tx in
                                    block[transactions_str]]

                    updated_block = Block(block[index_str], block[previous_hash_str], block[proof_str],
                                          converted_tx, block[timestamp_str])
                    updated_blockchain.append(updated_block)

                self.chain = updated_blockchain
                updated_transactions = []
                open_transaction = json.loads(file_content[1])[:-1]
                # converting json saved file into transactions objects
                for tx in open_transaction:
                    updated_transaction = Transaction(tx[sender_str], tx[recipient_str], tx[signature_str],
                                                      tx[amount_str])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
                peer_nodes = json.loads(file_content[2])
                self.__peer_node = set(peer_nodes)
        except (IOError, IndexError):
            pass
        return True

    # function to save date in exteranal drive
    def save_data(self):
        try:
            with open('blockchain-{}.dat'.format(self.node_id), mode='w') as f:
                save_able_chain = [block.__dict__ for block in
                                   [Block(block_el.index,
                                          block_el.previous_hash,
                                          block_el.proof,
                                          [tx.__dict__ for tx in block_el.transactions],
                                          block_el.timestamp) for block_el in
                                    self.__chain]]
                f.write(json.dumps(save_able_chain))
                f.write('\n')
                save_able_tx = [transactions.__dict__ for transactions in self.__open_transactions]

                f.write(json.dumps(save_able_tx))
                f.write('\n')
                f.write(json.dumps(list(self.__peer_node)))
        except IOError:
            print("Saving failed")

        # proof of work iteration and verifying logic

    def proof_of_work(self, transaction):
        # -1 for last block
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        # just increase nonce for valid_proof
        while not Verification.valid_proof(transaction, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self, sender=None):
        if sender is None:
            if self.public_key is None:
                return None
            participant_ = self.public_key
        else:
            participant_ = sender
        tx_sender = [[tx.amount for tx in block.transactions
                      if tx.sender == participant_] for block in self.__chain]

        open_tx_sender = [tx.amount for tx in self.__open_transactions
                          if tx.sender == participant_]

        tx_recipient = [[tx.amount for tx in block.transactions
                         if tx.recipient == participant_] for block in self.__chain]

        tx_sender.append(open_tx_sender)
        print(tx_sender)
        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender,
                             0)
        amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0,
                                 tx_recipient, 0)

        balance = round(amount_received - amount_sent, 13)
        return balance

    # last block needed for hashing
    def get_last_block_element(self):
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    # adding transaction in open transaction not in blockchain
    def add_transaction(self, sender_, recipient_, signature, amount_=0.0, receiving=False):
        if self.public_key is None:
            return False

        # transaction = {'sender': sender_,
        #                'recipient': recipient_,
        #                'amount': amount_
        #                }

        transaction = Transaction(sender_, recipient_, signature, amount_)
        # verifying transaction before adding in open transaction

        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            # saving transaction in blockchain external hard drive
            # if transaction is added in open_transaction  and not mine
            self.save_data()
            if not receiving:
                for node in self.__peer_node:
                    url = 'http://{}/broadcast-transaction'.format(node)
                    try:
                        response = requests.post(url, json={sender_str: sender_,
                                                            recipient_str: recipient_,
                                                            amount_str: amount_,
                                                            signature_str: signature
                                                            })
                        if response.status_code == 400 or response.status_code == 500:
                            print('Transaction declined needs resolving')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False

    def mine_block(self):
        if self.public_key is None:
            return None

        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)

        copied_open_transaction = self.__open_transactions[:]
        print("Failed transaction(s):\n")
        for tx in copied_open_transaction:
            if not Wallet.verify_transaction(tx):
                print(tx)
                print('\n')
                copied_open_transaction.remove(tx)

        proof = self.proof_of_work(copied_open_transaction)
        reward_transaction = Transaction('MINING', self.public_key, '', Mining_reward)

        copied_open_transaction.append(reward_transaction)

        block = Block(len(self.__chain), hashed_block, proof, copied_open_transaction)
        self.__chain.append(block)
        self.__open_transactions.clear()
        self.save_data()
        for node in self.__peer_node:
            url = 'http://{}/broadcast-block'.format(node)
            converted_block = block.__dict__.copy()
            converted_block[transactions_str] = [tx.__dict__ for tx in converted_block[transactions_str]]
            try:
                response = requests.post(url, json={'block': converted_block})
                print(response.status_code)
                if response.status_code == 400 or response.status_code == 500:
                    print('Block declined needs resolving')
                if response.status_code == 409:
                    self.resolve_conflict = True

            except requests.exceptions.ConnectionError:
                continue

        return block

    def add_block(self, block):
        transactions = [Transaction(tx[sender_str], tx[recipient_str], tx[signature_str], tx[amount_str]) for tx in
                        block[transactions_str]]
        proof_is_valid = Verification.valid_proof(transactions[:-1], block[previous_hash_str], block[proof_str])
        hashes_match = hash_block(self.chain[-1]) == block[previous_hash_str]
        if not proof_is_valid or not hashes_match:
            return False
        converted_block = Block(block[index_str], block[previous_hash_str], block[proof_str], transactions,
                                block[timestamp_str])
        self.__chain.append(converted_block)
        stored_transaction = self.__open_transactions[:]
        for itx in block[transactions_str]:
            for opentx in stored_transaction:
                if opentx.sender == itx[sender_str] and opentx.recipient == itx[recipient_str] and opentx.amount == \
                        itx[amount_str] and opentx.signature == itx[signature_str]:
                    try:
                        self.__open_transactions.remove(opentx)
                    except ValueError:
                        print('item is removed')

        self.save_data()
        return True

    def resolve(self):
        winner_chain = self.chain
        replace = False
        for node in self.__peer_node:
            url = 'http://{}/chain'.format(node)
            try:
                response = requests.get(url)
                node_chain = response.json()
                node_chain = [
                    Block(block[index_str], block[previous_hash_str], block[proof_str],
                          [Transaction(tx[sender_str], tx[recipient_str], tx[signature_str], tx[amount_str]) for tx in
                           block[transactions_str]], block[timestamp_str]) for block
                    in node_chain]

                node_chain_length = len(node_chain)
                local_chain_length = len(self.chain)
                if node_chain_length > local_chain_length and Verification.verify_chain(node_chain):
                    winner_chain = node_chain
                    replace = True

            except requests.exceptions.ConnectionError:
                continue
            self.resolve_conflict = False
            self.chain = winner_chain
            if replace:
                self.__open_transactions = []
            self.save_data()
            return replace

    def add_peer_node(self, node):
        self.__peer_node.add(node)
        self.save_data()

    def remove_peer_node(self, node):
        self.__peer_node.discard(node)
        self.save_data()

    def get_peer_node(self):
        return list(self.__peer_node)
