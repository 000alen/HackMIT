from exchange import buy, sell, get_blockchain, get_transactions, get_info
from blockchain import Block, Transaction, Blockchain
from utils import gen_uuid, post_route
from crypto import generate_keys
from constants import USERNAME, REWARD


def check_if_new_block(blockchain: Blockchain):
    new_chain = get_blockchain()
    if blockchain and new_chain and new_chain.head.get_hash() == blockchain.head.get_hash():
        blockchain = new_chain
        return False
    return True


def mine(blockchain, block: Block, start, end):
    """Keep guessing and checking the nonce in hopes
    we mine the provided block.
    """
    print("\n\n" + ("-" * 40))
    print("Mining now with %i transactions." % len(block.transactions))

    for i in range(start, end + 1):
        if check_if_new_block(blockchain):
            return False
    
        block.nonce = i
        if block.is_valid(): 
            break

    else:
        return False

    print("\nMined block:", block.get_hash(), "with nonce", block.nonce)
    return True


def run_miner(public, private, blockchain, start, end):
    """Run the main miner loop.
    """

    # Load transaction queue and blockchain from server.
    txns: list[Transaction] = get_transactions()
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
    result = mine(b, start, end)

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
