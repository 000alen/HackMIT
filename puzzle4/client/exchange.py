"""Main wallet code for HackCoin.
"""
from abc import get_cache_token
from typing import Union

from blockchain import Blockchain, Transaction
from crypto import generate_keys
from utils import post_route, gen_uuid, get_route, trim_string, jsonpickle_decode
from constants import PRINT_STR_LEN
from tabulate import tabulate


def create_public_private() -> tuple[str, str]:
    private, public = generate_keys()
    return public, private


def get_blockchain() -> Union[Blockchain, None]:
    resp = post_route('blockchain')
    if(resp):
        bc: Blockchain = jsonpickle_decode(resp["blockchain"])  # type: ignore
        bc._unflatten()
        return bc


def get_transactions() -> list[Transaction]:
    resp = get_route("transaction")
    if(resp and resp["success"]):
        return resp["data"]
    return []


def get_info() -> dict[str, Any]:
    resp = get_route('info')
    if(not resp):
        print("failed to fetch info")
    return resp["data"] if resp else {"cash": 0, "price": "?", "vendor": None}


def get_balance(public: str, blockchain) -> int:
    if not blockchain:
        print("unable to get blockchain")
        return 0
    return blockchain.get_balance(public)


def status(public: str) -> tuple[int, int, int]:
    info = get_info()
    return get_balance(public), info["cash"], info["price"]

    # print(
    #     f"You have: {str(get_balance(public))} hackcoins, and {info['cash']} dollars")
    # print(f"Current market price of Hackcoin: ${info['price']}")


def get_market_agents(public: str):
    resp = get_route("market")

    if(resp):
        data = resp["data"]
        data["me"] = public
        return data
    return {}


def transfer(public: str, private: str, receiver_public: str, amount: int) -> bool:
    if get_balance(public) < amount:
        # print("You don't have enough HackCoins.")
        return False

    # Build a new transaction.
    t = Transaction(
        id=gen_uuid(),
        sender=public,
        receiver=receiver_public,
        value=amount,
        signature=""
    )

    # Sign it.
    t.sign(private)

    post_route("transaction", {"transactions": [t]})

    return True


def buy(public: str, amount: int) -> bool:
    resp = get_route("buy", {"pubkey": public, "amount": amount})
    if(resp):
        if resp["success"]:
            # print(f"You successfully bought {amount} hackcoin!")
            # print("Transaction currently pending (check back later)")
            return True
        else:
            # print(f"Failed! {resp['message']}")
            return False


def sell(public: str, private: str, amount: int) -> bool:
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
            # print(f"You successfully sold {amount} hackcoin!")
            # print("Transaction currently pending (check back later)")
            return True
        else:
            # print(f"Failed! {resp['message']}")
            return False


def donate():
    resp = get_route("donate")
    if(resp):
        if resp["success"]:
            print(resp["message"])
            print("Thanks for playing!")
            return True
        else:
            print(f"Failed! {resp['message']}")
            return False


def print_transactions():
    txns = get_transactions()
    agents = get_market_agents()

    addr_to_name = {v: k for k, v in agents.items()}

    def name_lookup(addr):
        if addr in addr_to_name:
            return f"{trim_string(addr)} ({addr_to_name[addr]})"
        return trim_string(addr)

    print("Pending transactions:")
    print(tabulate([[trim_string(t.id), f"{name_lookup(t.sender)} -> {name_lookup(t.receiver)}", t.value]
          for t in txns], headers=["id", "transfer", "coins"]))


def print_blockchain(blockchain: Blockchain):
    agents = get_market_agents()
    agents = {v: k for k, v in agents.items()}
    rows = []
    for block in blockchain.traverse_blocks(blockchain.head):
        rows.append([trim_string(getattr(block, "miner", "anonymous"), PRINT_STR_LEN), trim_string(block.get_hash(), PRINT_STR_LEN), "\n".join(
            [t.pretty_print(PRINT_STR_LEN, agents) for t in block.transactions]), trim_string(block.previous_hash, PRINT_STR_LEN)])
    print(tabulate(rows[::-1], headers=["miner",
          "hash", "transactions", "prev_hash"]))


def print_market_agents(agents):
    print(tabulate(agents.items(), headers=["name", "public key"]))
