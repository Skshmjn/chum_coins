from blockchain import Blockchain
from util.verification import Verification
from wallet import Wallet


class Node:
    def __init__(self):
        # self.wallet.public_key = str(uuid4())
        self.wallet = Wallet()
        self.wallet.create_key()
        self.blockchain = Blockchain(self.wallet.public_key)

    # initial value getting
    def get_user_value(self):
        user_input_ = input("your choice: ")
        return user_input_

    # getting transaction details
    def get_transaction_value(self):
        tx_recipient = input("Enter the recipient of the transaction: ")
        txamount = float(input('Enter the amount: '))
        return (tx_recipient, txamount)

    # blockchain.append([last_transaction, transaction_amount])

    def print_blockchain_elements(self):
        for block in self.blockchain.chain:
            print("outputting block")
            print(block)
            print("\n")
        else:
            print('*' * 20 + "\n")

    def listen_for_input(self):
        waiting_for_input = True

        #   print("Balance of {}:{}".format(self.wallet.public_key, self.blockchain.get_balance()) + "\n")
        while waiting_for_input:
            print("Please choose \n")
            print("1: Add new transaction")
            print("2: Mine the blockchain blocks")
            print("3: Output the blockchain blocks")
            print("4: Verify all Transactions")
            print('5: Create wallet')
            print('6: Load wallet')
            print('7: Save wallet')
            print("q: Quit blockchain blocks")
            print('-' * 20)
            user_input = self.get_user_value()
            user_input = user_input.strip()
            print("\n")

            if user_input == "1":

                tx_data = self.get_transaction_value()
                recipient, amount = tx_data
                signature = self.wallet.sign_transaction(self.wallet.public_key, recipient, amount)
                if self.blockchain.add_transaction(self.wallet.public_key, recipient, signature, amount):
                    print('Added transaction')
                    print(self.blockchain.get_open_transaction())

                else:
                    print("Not enough coins")

            elif user_input == '2':
                if self.blockchain is None:
                    print("Don't have wallet. Create or load wallet")
                self.blockchain.mine_block()

            elif user_input == "3":

                self.print_blockchain_elements()
            # print(get_balance['Chum Chum'])

            elif user_input == '4':

                if Verification.verify_transactions(self.blockchain.get_open_transaction(),
                                                    self.blockchain.get_balance):
                    print("All transaction are verified")
                else:
                    print("Invalid transaction")
            elif user_input == '5':

                self.wallet.create_key()
                self.blockchain = Blockchain(self.wallet.public_key)

            elif user_input == '6':
                self.wallet.load_key()
                self.blockchain = Blockchain(self.wallet.public_key)

            elif user_input == '7':
                self.wallet.save_key()
            elif user_input == 'q' and 'Q':
                print("Exiting")
                waiting_for_input = False

            else:
                print("invalid")

            if not Verification.verify_chain(self.blockchain.chain):
                self.print_blockchain_elements()
                print("invalid block")
                waiting_for_input = False

            print("Balance of {}:{}".format(self.wallet.public_key, self.blockchain.get_balance()) + "\n")
        else:

            print("Terminated")

        print("done")

if __name__=='__main__':
    node = Node()
    node.listen_for_input()

