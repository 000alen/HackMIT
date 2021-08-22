"""Main wallet code for HackCoin.
"""
from abc import get_cache_token
import os
import sys
from typing import Optional, Union, List

import jsonpickle
from blockchain import Blockchain, Transaction
from crypto import generate_keys
from utils import post_route, gen_uuid, get_route, trim_string, jsonpickle_decode
from pyfiglet import Figlet
from constants import WALLET_FILE, PRINT_STR_LEN
from tabulate import tabulate

import os
import json

public: str = ""
private: str = ""
blockchain: Optional[Blockchain] = None

def print_header():
    """Why not.
    """
    f = Figlet(font='slant')
    print(f.renderText('HackBase'))

def load_or_create():
    """Load an existing wallet, or create a
    new one.
    """
    global public
    global private

    if os.path.exists(WALLET_FILE):
        # Load existing.
        with open(WALLET_FILE, 'r') as f:
            wallet_contents = f.read()
        wallet_obj = json.loads(wallet_contents)
        public = wallet_obj['public']
        private = wallet_obj['private']

        print("Loaded existing wallet from", WALLET_FILE)
    else:
        # Create a new address and dump it.
        private, public = generate_keys()

        wallet_contents = json.dumps({
            'public': public,
            'private': private
        })

        with open(WALLET_FILE, 'w') as f:
            f.write(wallet_contents)
        print("Created new wallet in", WALLET_FILE)
        
    print("Your wallet address is:", public)


def get_blockchain() -> Union[Blockchain, None]:
    resp = post_route('blockchain')
    if(resp):
        bc: Blockchain = jsonpickle_decode(resp["blockchain"]) # type: ignore
        bc._unflatten()
        return bc

def load_blockchain():
    """Loads the server blockchain state.
    """
    global blockchain
    blockchain = get_blockchain()

def get_transactions() -> List[Transaction]:
    resp = get_route("transaction")
    if(resp and resp["success"]):
        return resp["data"]
    return []

def get_info():
    resp = get_route('info')
    if(not resp):
        print("failed to fetch info")
    return resp["data"] if resp else {"cash": 0, "price": "?", "vendor": None}

def get_balance(address: str):
    load_blockchain()
    if not blockchain:
        print("unable to get blockchain")
        return 0
    return blockchain.get_balance(address)

def status(address: str):
    info = get_info()
    print(f"You have: {str(get_balance(address))} hackcoins, and {info['cash']} dollars")
    print(f"Current market price of Hackcoin: ${info['price']}")

def print_blockchain(bc: Blockchain):
    agents = get_market_agents()
    agents = {v:k for k, v in agents.items()}
    rows = []
    for block in bc.traverse_blocks(bc.head):
        rows.append([trim_string(getattr(block, "miner", "anonymous"), PRINT_STR_LEN), trim_string(block.get_hash(), PRINT_STR_LEN), "\n".join([t.pretty_print(PRINT_STR_LEN, agents) for t in block.transactions]), trim_string(block.previous_hash, PRINT_STR_LEN)])
    print(tabulate(rows[::-1], headers=["miner", "hash", "transactions", "prev_hash"]))
        
def get_market_agents():
    resp = get_route("market")
    
    if(resp):
        data = resp["data"]
        data["me"] = public
        return data
    return {}

def print_market_agents(agents):
    print(tabulate(agents.items(), headers=["name", "public key"]))

def print_transactions():
    txns = get_transactions()
    agents = get_market_agents()

    addr_to_name = {v:k for k,v in agents.items()}
    def name_lookup(addr):
        if addr in addr_to_name:
            return f"{trim_string(addr)} ({addr_to_name[addr]})"
        return trim_string(addr)

    print("Pending transactions:")
    print(tabulate([[trim_string(t.id), f"{name_lookup(t.sender)} -> {name_lookup(t.receiver)}", t.value] for t in txns], headers=["id", "transfer", "coins"]))


def transfer(receiver: str, amount: int, public: str, private: str):
    if get_balance(public) < amount:
        print("You don't have enough HackCoins.")
        return

    # Build a new transaction.
    t = Transaction(
        id = gen_uuid(),
        sender = public,
        receiver = receiver,
        value = amount,
        signature = ""
    )

    # Sign it.
    t.sign(private)

    post_route("transaction", {"transactions": [t]})


def buy(amount: int, public: str):
    resp = get_route("buy", {"pubkey": public, "amount": amount})
    if(resp):
        if resp["success"]:
            print(f"You successfully bought {amount} hackcoin!")
            print("Transaction currently pending (check back later)")
            return True
        else:
            print(f"Failed! {resp['message']}")
            return False 

def sell(amount: int, public: str, private: str):
    """The vendor requires you to publish the transaction before they send the money"""
    info = get_info()
    vendor = info["vendor"]

    # create transaction 
    txn_id = gen_uuid()
    t = Transaction(txn_id, public, vendor, amount, signature = "")
    t.sign(private)

    # publish transaction
    post_route("transaction", {"transactions": [t]})

    # send sell request, with transaction id
    resp = get_route("sell", {"pubkey": public, "amount": amount, "txn_id": txn_id})
    if(resp):
        if resp["success"]:
            print(f"You successfully sold {amount} hackcoin!")
            print("Transaction currently pending (check back later)")
        else:
            print(f"Failed! {resp['message']}")

def donate():
    resp = get_route("donate")
    if(resp):
        if resp["success"]:
            print(resp["message"])
            f = Figlet(font='standard')
            print(f.renderText("Thanks for playing!"))
            return True
        else:
            print(f"Failed! {resp['message']}")
            return False 

def start_repl():
    global public

    while True:
        command = input("> ").split()
        if len(command) == 0:
            print("Type a valid command.")
        elif command[0] == 'help' or command[0] == 'halp':
            print("Read README.md")
        elif command[0] == 'quit':
            break
        elif command[0] == 'status':
            address = public
            if len(command) >= 2:
                address = command[1]
            status(address)
        elif command[0] == 'bc':
            address = public
            load_blockchain()
            if(blockchain):
                print_blockchain(blockchain)
        elif command[0] == 'transfer':
            if len(command) < 3:
                print("Invalid syntax, it's transfer <payee> <amount>")
                continue
            payee = command[1]
            amount = int(command[2])
            transfer(payee, amount, public, private)
        elif command[0] == 'who':
            print_market_agents(get_market_agents())
        elif command[0] == 'txns':
            print_transactions()
        elif command[0] == 'buy':
            if len(command) < 2:
                print("Invalid syntax, it's buy <amount>")
                continue
            buy(int(command[1]), public)
        elif command[0] == 'sell':
            if len(command) < 2:
                print("Invalid syntax, it's sell <amount>")
                continue
            sell(int(command[1]), public, private)
        elif command[0] == 'donate':
            donate()


if __name__ == "__main__":
    print_header()
    load_or_create()

    start_repl()