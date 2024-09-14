import hashlib    # Used for hashing blocks
import json       # Used for manipulating data
from time import time  # Used to get the current Unix timestamp for the block
from urllib.parse import urlparse  # Helps parse URLs when registering new nodes
from uuid import uuid4  # Generates unique node identifiers
from flask import Flask, jsonify, request  # Used for creating the API framework
import requests  # Used to send requests for conflict resolution

# Define a class to represent the blockchain
class Blockchain:
    def __init__(self):
        self.chain = []  # List to store the chain of blocks
        self.current_transactions = []  # List to store current transactions
        self.nodes = set()  # Set to store the list of network nodes
        self.new_block(previous_hash='1', proof=100)  # Create the genesis block (first block in the chain)

    # Register a new node to the blockchain network
    def register_node(self, address):
        """
        Adds a new node to the network.
        :param address: Address of the node (e.g., 'http://192.168.0.5:5000')
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)  # Add node to the network

    # Check the validity of the blockchain
    def valid_chain(self, chain):
        """
        Check if a given blockchain is valid by verifying hashes and proofs of work.
        :param chain: The blockchain to validate
        :return: True if valid, False if not
        """
        last_block = chain[0]  # Start with the first block
        current_index = 1

        while current_index < len(chain):  # Loop through the blockchain
            block = chain[current_index]

            # Check if the previous hash of the current block matches the hash of the last block
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check if the proof of work is valid
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            # Move to the next block
            last_block = block
            current_index += 1

        return True

    # Resolve conflicts using the longest chain rule
    def resolve_conflicts(self):
        """
        Consensus algorithm: resolves conflicts by replacing our chain with the longest valid chain in the network.
        :return: True if our chain was replaced, False if not
        """
        neighbours = self.nodes  # Get all the neighboring nodes
        new_chain = None
        max_length = len(self.chain)  # Current chain length

        # Get and verify the chains from all the nodes in the network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Replace our chain if a longer valid chain is found
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace current chain if a new valid chain is found
        if new_chain:
            self.chain = new_chain
            return True

        return False

    # Create a new block and add it to the blockchain
    def new_block(self, proof, previous_hash=None):
        """
        Create a new block in the blockchain.
        :param proof: The proof of work
        :param previous_hash: The hash of the previous block
        :return: New block
        """
        block = {
            'index': len(self.chain) + 1,  # Block number
            'timestamp': time(),  # Current timestamp
            'transactions': self.current_transactions,  # Transactions in the block
            'proof': proof,  # Proof of work
            'previous_hash': previous_hash or self.hash(self.chain[-1]),  # Hash of the previous block
        }

        # Reset the list of current transactions
        self.current_transactions = []

        # Append the new block to the blockchain
        self.chain.append(block)
        return block

    # Add a new transaction to the list of transactions
    def new_transaction(self, sender, recipient, amount):
        """
        Create a new transaction.
        :param sender: Address of the sender
        :param recipient: Address of the recipient
        :param amount: Amount to transfer
        :return: Index of the block that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

    # Create a hash of the block
    @staticmethod
    def hash(block):
        """
        Create a SHA-256 hash of a block.
        :param block: Block
        :return: Hash value of the block
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    # Return the last block in the chain
    @property
    def last_block(self):
        return self.chain[-1]

    # Proof of work algorithm
    def proof_of_work(self, last_proof):
        """
        Simple proof of work algorithm:
        - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous proof, and p' is the new proof.
        :param last_proof: Previous proof
        :return: New proof
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    # Validate proof
    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validate the proof of work: Does hash(last_proof, proof) contain 4 leading zeroes?
        :param last_proof: Previous proof
        :param proof: Current proof
        :return: True if valid, False otherwise
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

# Instantiate the Node (API instance)
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

# Endpoint to mine a new block
@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Reward the miner (sender is "0" as it's a mining reward)
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Add the new block to the chain
    block = blockchain.new_block(proof)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

# Endpoint to create a new transaction
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Add the transaction to the blockchain
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

# Endpoint to return the full blockchain
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

# Endpoint to register new nodes
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

# Endpoint to resolve conflicts between nodes
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

# Run the Flask server to enable API access to the blockchain
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)