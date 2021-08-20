import hashlib 
import datetime
import json
from utils import trim_string
from time import time
from typing import Union, List
import constants
import crypto
import jsonpickle

class Transaction:
    def __init__(self, id: str, sender: str, receiver: str, value: int, signature: str):
        self.id = id
        self.sender = sender
        self.receiver = receiver
        self.value = value
        self.signature = signature 

    def __str__(self):
        return json.dumps({
            'id': self.id,
            'sender': self.sender,
            'receiver': self.receiver,
            'value': self.value,
            'signature': self.signature
        })
    
    def pretty_print(self, max_str_len=None, agents=None):
        sender = agents[self.sender] if agents and self.sender in agents else self.sender
        receiver = agents[self.receiver] if agents and self.receiver in agents else self.receiver

        if(not max_str_len):
            return f"[id: {self.id}, {sender} -> {receiver}, {self.value} coins]"
        return f"[id: {trim_string(self.id, max_str_len//2)}, {trim_string(sender, max_str_len)} -> {trim_string(receiver, max_str_len)}, {self.value} coins]"
    
    def comp(self):
        return json.dumps({
            'id': self.id,
            'sender': self.sender,
            'receiver': self.receiver,
            'value': self.value,
        })

    def valid_signature(self):
        if self.sender == "mined":
            return True
        return crypto.verify(self.comp(), self.sender, self.signature)

    def to_json(self):
        return {
            'id': self.id,
            'sender': self.sender,
            'receiver': self.receiver,
            'value': self.value,
            'signature': self.signature
        }
    
    @staticmethod
    def from_json(jobj):
        return Transaction(
            id = str(jobj['id']),
            sender = jobj['sender'],
            receiver = jobj['receiver'],
            value = int(jobj['value']),
            signature = jobj['signature']
        )
    
    def sign(self, private):
        self.signature = crypto.sign(self.comp(), private)



class Block:
    def __init__(self, transactions: List[Transaction], previous_hash: str, miner = "Anonymous", nonce: int = 0, height: int = -1, timestamp = int(time())):
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce 
        self.height = height
        self.miner = miner

        self.parent: Union[Block, None] = None
        self.parent_hash: str = ""

        self.transaction_map = {txn.comp() for txn in self.transactions}

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)
        self.transaction_map.add(transaction.comp())

    def get_hash_str(self):
        return f"{self.timestamp}{[str(t) for t in self.transactions]}{self.previous_hash}{self.nonce}".encode()

    def get_hash(self):
        sha = hashlib.sha256(self.get_hash_str())
        return sha.hexdigest()
    
    def set_parent(self, parent):
        self.parent = parent
        self.height = parent.height + 1

    def print_transactions(self):
        for tr in self.transactions:
            print(str(tr))
    
    def is_valid(self):
        return int(self.get_hash(), 16) < constants.DIFFICULTY

    def __str__(self):
        return json.dumps({
            'timestamp': str(self.timestamp),
            'transactions': [str(t) for t in self.transactions],
            'previous_hash': str(self.previous_hash),
            'nonce': self.nonce
        })
    
    def to_json(self):
        return {
            'timestamp': self.timestamp,
            'transactions': [t.to_json() for t in self.transactions],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }


    @staticmethod
    def from_json(jobj):
        return Block(
            timestamp = int(jobj['timestamp']),
            transactions = [
                Transaction.from_json(tj)
                for tj in jobj['transactions']
            ],
            previous_hash = str(jobj['previous_hash']),
            nonce = int(jobj['nonce'])
        )


def create_genesis_block():
    return Block( [], "")

class Blockchain:
    def __init__(self):
        first_block = create_genesis_block()

        self.head = first_block 
        self.blocks = {first_block.get_hash(): first_block}

    

    def traverse_blocks(self, head: Block, include_head=True):
        if include_head:
            yield head
        current = head.parent
        genisis_hash: str = create_genesis_block().get_hash()
        while current != None and current.get_hash() != genisis_hash:
            yield current
            current = current.parent

    def get_balance(self, address: str) -> int:
        total = 0

        for block in self.traverse_blocks(self.head, include_head=True):
            if not block:
                break
            
            for txn in block.transactions:
                if txn.sender == address and txn.receiver != address:
                    total -= txn.value
                elif txn.sender != address and txn.receiver == address:
                    total += txn.value
        return total

    def add_block(self, block: Block, cheat=False):
        """Checks the entire chain for valid transactions
        and checks proof of work. Then adds block."""

        block_hash = block.get_hash()

        # We already know this block.
        if block_hash in self.blocks:
            return False, "Known block.", {}
        
        # Parent doesn't exist :(
        if block.previous_hash not in self.blocks:
            return False, "No valid parent.", {}
        parent = self.blocks[block.previous_hash]
        block.set_parent(parent)

        # Check proof of work ;o
        if not cheat and not block.is_valid():
            return False, "Invalid proof of work.", {}

        # Verify transaction signatures.
        for transaction in block.transactions:
            if transaction.sender != "mined" and not transaction.valid_signature():
                return False, "Transaction has invalid signature.", {"txn": transaction}

        # Have any of these transactions been replays?
        for b in self.traverse_blocks(block, include_head=False):
            for c_txn in block.transactions:
                if c_txn.comp() in b.transaction_map:
                    # We found the same transaction in a previous block.
                    return False, "Transaction replay detected.", {"txn": c_txn}
        
        # For every transaction, does the sender own this money?
        reward_counted = False
        running_balance = {}
        for txn in block.transactions:
            if txn.value < 0:
                return False, "Amount can't be negative.", {"txn": txn}
            
            if txn.sender not in running_balance:
                running_balance[txn.sender] = 0

            if txn.sender == "mined":
                # This is the miner reward, let's make sure
                # it's correct. Technically, the miner can make
                # this payment to anyone she likes.
                if not cheat and txn.value > constants.REWARD:
                    return False, "Incorrect miner reward.", {"txn": txn}
                
                # Let's also make sure the reward is only given
                # once and once only.
                if reward_counted:
                    return False, "Miner reward found twice in block.", {"txn": txn}

                reward_counted = True
                running_balance[txn.sender] += constants.REWARD
            else:
                sender_coins = self.get_balance(txn.sender) + running_balance[txn.sender]
                print("sender balance: ", sender_coins)
                print("value: ", txn.value)
                if sender_coins < txn.value:
                    # sender doesn't have enough coins,
                    # block is invalid.
                    return False, "sender doesn't have enough coins.", {"txn": txn}
                running_balance[txn.sender] -= txn.value
        
        # Looks like everything is set with this block.
        # Let's add this block and compute the longest
        # chain.

        self.blocks[block_hash] = block
        if block.height > self.head.height:
            self.head = block
        
        return True, "Block added.", {}

    def to_json(self):
        return jsonpickle.encode(self)
        
    # needs to flatten Block linked list to be serializable
    def _flatten(self):
        for block in self.blocks.values():
            if(block.parent):
                block.parent_hash = block.parent.get_hash()
                block.parent = None

    def _unflatten(self):
        for block in self.blocks.values():
            try:
                block.parent_hash 
            except:
                block.parent_hash = ""
            if(block.parent_hash):
                block.parent = self.blocks[block.parent_hash] #type: ignore