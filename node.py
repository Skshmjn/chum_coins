from flask import Flask, jsonify, request, send_from_directory
from wallet import Wallet
from flask_cors import CORS
from blockchain import Blockchain

recipient_str = 'recipient'
sender_str = 'sender'
signature_str = 'signature'
amount_str = 'amount'
transactions_str = 'transactions'
app = Flask(__name__)

CORS(app)


@app.route('/', methods=['GET'])
def get_ui():
    return send_from_directory('ui', 'node.html')


@app.route('/network', methods=['GET'])
def get_network_ui():
    return send_from_directory('ui', 'network.html')


@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_key()
    if wallet.save_key():
        # setting blockchain with public key and port
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }

        return jsonify(response), 201
    else:
        response = {
            'message': 'saving the keys failed'
        }
        return jsonify(response), 500


@app.route('/wallet', methods=['GET'])
def load_keys():
    if wallet.load_key():
        # setting blockchain with public key and port
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }

        return jsonify(response), 201
    else:
        response = {
            'message': 'loading the keys failed'
        }
        return jsonify(response), 500


@app.route('/transactions', methods=['GET'])
def get_opentransaction():
    transactions = blockchain.get_open_transaction()
    dict_transaction = [tx.__dict__ for tx in transactions]
    return jsonify(dict_transaction), 200


@app.route('/balance', methods=['GET'])
def get_balance():
    balance = blockchain.get_balance()
    if balance != None:
        response = {
            'message': 'Fetched balance successfully',
            'funds': balance
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Loading balance failed',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500


@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key == None:
        response = {
            'message': 'No wallet set up'
        }
        return jsonify(response), 400
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found'
        }
        return jsonify(response), 400
    required_fields = [recipient_str, amount_str]
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Required data is missing'
        }
        return jsonify(response), 400

    recipient = values[recipient_str]
    amount = values[amount_str]
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
    success = blockchain.add_transaction(wallet.public_key, recipient, signature, amount)
    if success:
        response = {
            'message': 'Successfully added a transactions',
            transactions_str: {
                sender_str: wallet.public_key,
                recipient_str: recipient,
                amount_str: amount,
                signature_str: signature

            },
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 200

    else:
        response = {
            'message': 'creating a transactions failed'
        }
        return jsonify(response), 500


@app.route('/mine', methods=['POST'])
def mine():
    if blockchain.resolve_conflict:
        response = {'message': 'Resolve conflict first'}
        return jsonify(response), 409

    block = blockchain.mine_block()

    if block != None:
        dict_block = block.__dict__.copy()
        dict_block[transactions_str] = [tx.__dict__ for tx in dict_block[transactions_str]]
        response = {
            'message': 'adding a block successfully',
            'wallet_set_up': dict_block,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'adding a block failed',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500


@app.route('/resolve', methods=['POST'])
def resolve_conflict():
    replaced=blockchain.resolve()
    if replaced:
        response={'message':'Chain was replaced'}
    else:
        response = {'message': 'Chain was not replaced'}
    return jsonify(response),200

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block[transactions_str] = [tx.__dict__ for tx in dict_block[transactions_str]]
    return jsonify(dict_chain), 200


@app.route('/node', methods=['POST'])
def add_node():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data attached'
        }
        return jsonify(response), 400

    if 'node' not in values:
        response = {
            'message': 'No Node data attached'
        }
        return jsonify(response), 400
    node = values['node']
    blockchain.add_peer_node(node)
    response = {
        'message': 'Node added successfully',
        'all_nodes': blockchain.get_peer_node()

    }
    return jsonify(response), 201


@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    if node_url == '' or node_url == None:
        response = {
            'message': 'No Node is found'
        }
        return jsonify(response), 400

    blockchain.remove_peer_node(node_url)
    response = {
        'message': 'node removed',
        'all_nodes': blockchain.get_peer_node()
    }

    return jsonify(response), 200


@app.route('/node', methods=['GET'])
def get_node():
    nodes = blockchain.get_peer_node()
    response = {
        'all_nodes': nodes
    }
    return jsonify(response), 200


@app.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found'
        }
        return jsonify(response), 400
    required = {sender_str, recipient_str, amount_str, signature_str}
    if not all(key in values for key in required):
        response = {
            'message': 'some data not found'
        }
        return jsonify(response), 400
    success = blockchain.add_transaction(values[sender_str], values[recipient_str], values[signature_str],
                                         values[amount_str], receiving=True)
    if success:
        response = {
            'message': 'Successfully added a transactions',
            transactions_str: {
                sender_str: values[sender_str],
                recipient_str: values[recipient_str],
                amount_str: values[amount_str],
                signature_str: values[signature_str]

            }
        }
        return jsonify(response), 200

    else:
        response = {
            'message': 'creating a transactions failed'
        }
        return jsonify(response), 500


@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found'
        }
        return jsonify(response), 400
    if 'block' not in values:
        response = {
            'message': 'some data not found'
        }
        return jsonify(response), 400
    block = values['block']
    if block['index'] == blockchain.chain[-1].index + 1:
        if blockchain.add_block(block):
            response = {'message': 'block added'}
            return jsonify(response), 201
        else:
            response = {
                'message': 'Block seems invalid'
            }
            return jsonify(response), 409

    elif block['index'] > blockchain.chain[-1].index:
        response = {
            'message': 'blockchain is different'
        }
        blockchain.resolve_conflict = True

        return jsonify(response), 200
    else:
        response = {
            'message': 'blockchain is complete'
        }
        return jsonify(response), 409


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(port)
    # public key is none as no wallet is created or loaded
    # it is done to print blockchain
    blockchain = Blockchain(wallet.public_key, port)
    app.run(host='0.0.0.0', port=port)
