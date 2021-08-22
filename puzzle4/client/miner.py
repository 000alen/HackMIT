
import os
from exchange import buy, sell, get_blockchain, get_transactions, get_info
from time import time
from typing import Optional, List
from blockchain import Block, Transaction, Blockchain, create_genesis_block
from utils import gen_uuid, post_route
from crypto import generate_keys
from constants import USERNAME, WALLET_FILE, REWARD
from pyfiglet import Figlet

import datetime
import json
import os

public: str = ""
private: str = ""
blockchain: Optional[Blockchain] = None

def print_header():
    """Why not.
    """
    f = Figlet(font='big')
    print(f.renderText('HackMiner 2.0'))
    print("Version 2.2.1")

def try_mine(block: Block):
    """Updates the nonce and sees if it's valid.
    """
    block.nonce += 1
    return block.is_valid()

def check_if_new_block():
    global blockchain
    new_chain = get_blockchain()
    if blockchain and new_chain and new_chain.head.get_hash() == blockchain.head.get_hash():
        blockchain = new_chain 
        return False 
    return True

def mine(block: Block):
    """Keep guessing and checking the nonce in hopes
    we mine the provided block.
    """
    print("\n\n" + ("-" * 40))
    print("Mining now with %i transactions." % len(block.transactions))
    hashes_done = 0

    start = datetime.datetime.now()
    while not try_mine(block):
        hashes_done += 1

        if hashes_done % 300000 == 0:
            end = datetime.datetime.now()
            seconds = (end - start).total_seconds()

            print("Hash Rate: %i hashes/second      \r" % (300000 / seconds),)
            
            if(check_if_new_block()):
                return False
            start = datetime.datetime.now()

    print("\nMined block:", block.get_hash(), "with nonce", block.nonce)
    return True

def load_wallet():
    """Load the wallet.json file and load the
    keys from there.
    """

    global public
    global private

    if os.path.exists(WALLET_FILE):
        with open(WALLET_FILE, 'r') as f:
            wallet_json = f.read()
        wallet_obj = json.loads(wallet_json)

        public = wallet_obj['public']
        private = wallet_obj['private']
    else:
        print("First run the exchange.py file!")
        exit()
           
def run_sample():
    """Testing code.
    """
    # Mine a sample block.
    b = Block(
        transactions = [],
        previous_hash = create_genesis_block().get_hash()
    )

    mine(b)
    
     

def run_miner():
    """Run the main miner loop.
    """

    global blockchain
    global public
    global private

    while True:
        # Load transaction queue and blockchain from server.
        txns: List[Transaction] = get_transactions()
        blockchain = get_blockchain()

        if not blockchain:
            print("Unable to fetch blockchain")
            return;
        
        # Add reward to us yay.
        reward = Transaction(
            id = gen_uuid(),
            sender = "mined",
            receiver = public,
            value = REWARD,
            signature = ""
        )
        reward.sign(private)
        txns.append(reward)

        # Construct a new block.
        b = Block(
            transactions = txns,
            previous_hash = blockchain.head.get_hash(),
            miner = USERNAME
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
            if resp and resp['success']: #type: ignore
                print("Block added!")
            else:
                print("Couldn't add block:", resp['message']) #type: ignore
        else:
            print("Someone else mined the block before us :(")


if __name__ == '__main__':
    print_header()
    load_wallet()
    run_miner()