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
from constants import PRINT_STR_LEN
from tabulate import tabulate

import os
import json


def create_wallet(wallet_file=None):
    # Create a new address and dump it.
    private, public = generate_keys()

    if wallet_file is not None:

        wallet_contents = json.dumps({
            'public': public,
            'private': private
        })

        with open(wallet_file, 'w') as f:
            f.write(wallet_contents)
        print("Created new wallet in", wallet_file)
    print("Your wallet address is:", public)

    return public, private


def get_wallet(wallet_file):
    # Load existing.
    with open(wallet_file, 'r') as f:
        wallet_contents = f.read()
    wallet_obj = json.loads(wallet_contents)
    public = wallet_obj['public']
    private = wallet_obj['private']

    print("Loaded existing wallet from", wallet_file)

    return public, private


def get_blockchain() -> Union[Blockchain, None]:
    resp = post_route('blockchain')
    if(resp):
        bc: Blockchain = jsonpickle_decode(resp["blockchain"])  # type: ignore
        bc._unflatten()
        return bc


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


def get_balance(address: str, blockchain):
    if not blockchain:
        print("unable to get blockchain")
        return 0
    return blockchain.get_balance(address)


def status(address: str, blockchain):
    info = get_info()
    print(
        f"You have: {str(get_balance(address, blockchain))} hackcoins, and {info['cash']} dollars")
    print(f"Current market price of Hackcoin: ${info['price']}")


def print_blockchain(bc: Blockchain):
    agents = get_market_agents()
    agents = {v: k for k, v in agents.items()}
    rows = []
    for block in bc.traverse_blocks(bc.head):
        rows.append([trim_string(getattr(block, "miner", "anonymous"), PRINT_STR_LEN), trim_string(block.get_hash(), PRINT_STR_LEN), "\n".join(
            [t.pretty_print(PRINT_STR_LEN, agents) for t in block.transactions]), trim_string(block.previous_hash, PRINT_STR_LEN)])
    print(tabulate(rows[::-1], headers=["miner",
          "hash", "transactions", "prev_hash"]))


def get_market_agents(public):
    resp = get_route("market")

    if(resp):
        data = resp["data"]
        data["me"] = public
        return data
    return {}


def transfer(receiver: str, amount: int, public: str, private: str):
    if get_balance(public, get_blockchain()) < amount:
        print("You don't have enough HackCoins.")
        return

    # Build a new transaction.
    t = Transaction(
        id=gen_uuid(),
        sender=public,
        receiver=receiver,
        value=amount,
        signature=""
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
    t = Transaction(txn_id, public, vendor, amount, signature="")
    t.sign(private)

    # publish transaction
    post_route("transaction", {"transactions": [t]})

    # send sell request, with transaction id
    resp = get_route(
        "sell", {"pubkey": public, "amount": amount, "txn_id": txn_id})
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

def print_market_agents(agents):
    print(tabulate(agents.items(), headers=["name", "public key"]))


def print_transactions(txns):
    agents = get_market_agents()

    addr_to_name = {v: k for k, v in agents.items()}

    def name_lookup(addr):
        if addr in addr_to_name:
            return f"{trim_string(addr)} ({addr_to_name[addr]})"
        return trim_string(addr)

    print("Pending transactions:")
    print(tabulate([[trim_string(t.id), f"{name_lookup(t.sender)} -> {name_lookup(t.receiver)}", t.value]
          for t in txns], headers=["id", "transfer", "coins"]))
