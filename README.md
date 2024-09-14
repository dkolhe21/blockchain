
---

# Blockchain Implementation with Flask

This project implements a simple blockchain using Python and Flask. The blockchain supports basic features like mining new blocks, adding transactions, and resolving conflicts between different blockchain nodes using a consensus algorithm.

## Features

- **Mine New Blocks**: A proof-of-work algorithm is used to mine new blocks.
- **Transaction Management**: You can add new transactions to be recorded in the next mined block.
- **Consensus Algorithm**: Resolves conflicts between nodes by ensuring that the longest valid chain is accepted.
- **RESTful API**: A Flask API is provided to interact with the blockchain.

## Prerequisites

- Python 3.x
- Flask
- Requests

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-repo/blockchain-flask.git
cd blockchain-flask
```

### 2. Install the required dependencies

To install the required dependencies, use the following command:

```bash
pip install -r requirements.txt
```

### 3. Run the application

Once all dependencies are installed, run the Flask server using:

```bash
python blockchain.py
```

The server will start on `http://127.0.0.1:5000/` by default.

## API Endpoints

### 1. `/mine` (GET)

Mines a new block using proof-of-work and adds it to the chain.

**Response**:
```json
{
    "message": "New Block Forged",
    "index": 1,
    "transactions": [],
    "proof": 12345,
    "previous_hash": "abcdef"
}
```

### 2. `/transactions/new` (POST)

Adds a new transaction to be included in the next block.

**Request**:
```json
{
    "sender": "address1",
    "recipient": "address2",
    "amount": 10
}
```

**Response**:
```json
{
    "message": "Transaction will be added to Block 2"
}
```

### 3. `/chain` (GET)

Returns the full blockchain.

**Response**:
```json
{
    "chain": [...],
    "length": 2
}
```

### 4. `/nodes/register` (POST)

Registers new nodes in the network.

**Request**:
```json
{
    "nodes": ["http://127.0.0.1:5001"]
}
```

**Response**:
```json
{
    "message": "New nodes have been added",
    "total_nodes": ["127.0.0.1:5001"]
}
```

### 5. `/nodes/resolve` (GET)

Resolves conflicts by replacing the current chain with the longest one.

**Response**:
```json
{
    "message": "Our chain was replaced",
    "new_chain": [...]
}
```

---


### `requirements.txt`

```txt
Flask==2.0.3
requests==2.26.0