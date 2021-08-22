
import os
from time import time
from typing import Optional, List
from itertools import count

from exchange import buy, sell, get_blockchain, get_transactions, get_info
from blockchain import Block, Transaction, Blockchain, create_genesis_block
from utils import gen_uuid, post_route
from crypto import generate_keys
from constants import USERNAME, WALLET_FILE, REWARD

import datetime
import json
import os


def try_mine(block: Block, nonce=None):
    """Updates the nonce and sees if it's valid.
    """
    if nonce is None:
        block.nonce += 1
    else:
        block.nonce = nonce
    return block.is_valid()


def check_if_new_block(blockchain):
    new_chain = get_blockchain()
    if blockchain and new_chain and new_chain.head.get_hash() == blockchain.head.get_hash():
        blockchain = new_chain
        return False
    return True


def mine(block: Block, left=None, right=None, messages_queue=None):
    """Keep guessing and checking the nonce in hopes
    we mine the provided block.
    """
    # print("\n\n" + ("-" * 40))
    # print("Mining now with %i transactions." % len(block.transactions))
    hashes_done = 0

    start = datetime.datetime.now()

    if left is None and right is None:
        iterator = count(0)
    else:
        iterator = range(left, right + 1)

    for i in iterator:
        if try_mine(block, nonce=i):
            break

        hashes_done += 1

        if hashes_done % 300000 == 0:
            end = datetime.datetime.now()
            seconds = (end - start).total_seconds()

            hash_rate = (300000 / seconds)
            print("Hash Rate: %i hashes/second      \r" % hash_rate)
            # messages_queue.put("HASH_RATE_%i" % hash_rate)

            if(check_if_new_block()):
                return False
            start = datetime.datetime.now()

    # print("\nMined block:", block.get_hash(), "with nonce", block.nonce)
    return True


def run_miner(public, private):
    """Run the main miner loop.
    """

    while True:
        # Load transaction queue and blockchain from server.
        txns: List[Transaction] = get_transactions()
        blockchain = get_blockchain()

        if not blockchain:
            print("Unable to fetch blockchain")
            return

        # Add reward to us yay.
        reward = Transaction(
            id=gen_uuid(),
            sender="mined",
            receiver=public,
            value=REWARD,
            signature=""
        )
        reward.sign(private)
        txns.append(reward)

        # Construct a new block.
        b = Block(
            transactions=txns,
            previous_hash=blockchain.head.get_hash(),
            miner=USERNAME
        )

        # Let's mine this block.
        result = mine(b)

        # Is this _the_ new block?
        # or did the server swoop us :(
        new_chain = get_blockchain()

        if result and new_chain and new_chain.head.get_hash() == blockchain.head.get_hash():
            # WE MINED THIS BLOCK YAY.
            # AND WE WIN.
            resp = post_route('add', data=b)
            if resp and resp['success']:  # type: ignore
                print("Block added!")
            else:
                print("Couldn't add block:", resp['message'])  # type: ignore
        else:
            print("Someone else mined the block before us :(")


def mining_worker(public, private, tasks_queue, messages_queue):
    while True:
        try:
            left, right = tasks_queue.get_nowait()
        except:
            continue

        transactions = get_transactions()
        blockchain = get_blockchain()

        if not blockchain:
            messages_queue.put("NO_BLOCKCHAIN")
            left, right = None, None

        reward = Transaction(
            id=gen_uuid(),
            sender="mined",
            receiver=public,
            value=REWARD,
            signature=""
        )
        reward.sign(private)
        transactions.append(reward)

        b = Block(
            transactions=transactions,
            previous_hash=blockchain.head.get_hash(),
            miner=USERNAME
        )

        result = mine(b, left, right, messages_queue)

        new_chain = get_blockchain()

        if result and new_chain and new_chain.head.get_hash() == blockchain.head.get_hash():
            resp = post_route('add', data=b)
            if resp and resp['success']:  # type: ignore
                messages_queue.put("BLOCK_MINED")
            else:
                messages_queue.put("BLOCK_MINE_FAILED")
        elif result and new_chain and new_chain.head.get_hash() != blockchain.head.get_hash():
            messages_queue.put("BLOCK_ALREADY_MINED")
        else:
            messages_queue.put("BLOCK_NOT_MINED")
