from Crypto.PublicKey import RSA
import Crypto.Random
import binascii
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256


class Wallet:
    def __init__(self, node_id):
        # initial constructor for just displaying blockchain and wallet is defined earlier as blockchain needs a wallet
        self.node_id = node_id
        self.private_key = None
        self.public_key = None

    def create_key(self):
        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key

    def save_key(self):
        if self.private_key is not None and self.public_key is not None:
            try:
                with open("wallet-{}.dat".format(self.node_id), mode="w") as f:
                    f.write(self.public_key)
                    f.write("\n")
                    f.write(self.private_key)
                return True
            except(IOError, IndexError):
                print("Saving wallet failed")
                return False

    def load_key(self):
        try:
            with open("wallet-{}.dat".format(self.node_id), mode="r") as f:
                keys = f.readlines()
                public_key = keys[0][:-1]
                private_key = keys[1]
                self.public_key = public_key
                self.private_key = private_key
            return True

        except(IOError, IndexError):
            print("Loading wallet failed")
            return False

    @staticmethod
    def generate_keys():
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        return (binascii.hexlify(private_key.export_key(format='DER')).decode('ascii'),
                binascii.hexlify(public_key.export_key(format='DER')).decode('ascii'))

    def sign_transaction(self, sender, recipient, amount):
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        ha = SHA256.new((str(sender) + str(recipient) + str(amount)).encode('utf8'))

        signature = signer.sign(ha)
        return binascii.hexlify(signature).decode('ascii')

    @staticmethod
    def verify_transaction(transaction):

        if transaction.sender == "MINING":
            return False

        verifier = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(transaction.sender)))
        ha = SHA256.new((str(transaction.sender) + str(transaction.recipient) + str(transaction.amount)).encode('utf8'))

        return verifier.verify(ha, binascii.unhexlify(transaction.signature))
