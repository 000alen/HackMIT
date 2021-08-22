# HackBase Client Code

The document will outline the basic structure, setup and use of the HackBase client.

## Setup

The client code is written in Python 3.9. Please make sure your python version is 3.5 and above.

We would recommend using a virtual environment. In the project directory:

```
pip3 install virtualenv
virtualenv venv
source venv/bin/activate
```

Get dependencies,

```
pip3 install -r requirements.txt
```

## Running

First run the exchange client,

```
python3 exchange.py
```

This should generate a new blockchain address and store it in `wallet.json`. Once you have the address, the client will reuse this file.

Then in another terminal launch the miner,

```
python3 miner.py
```

The miner also looks for the `wallet.json` file and will cry if you can't provide it. The miner runs in the background and mines blocks.

## Exchange

The HackBase exchange provdies a variety of tools to transact your hackcoin. Here are the commands you can use

## Constants

The `constants.py` file should already come set up with the correct values. If it isn't, set it up as follows:

```python
NODE_SERVER = "<url of blockchain>/"

USERNAME = "<username>"

DIFFICULTY = 6

REWARD = 10

WALLET_FILE = "wallet.json"

STARTING_PRICE = 2

PRINT_STR_LEN = 20
```

Note that the difficulty only applies to you as the client. The server can _cheat_ the difficulty and you'd be forced to accept those blocks as valid since you're trying to buy something from the store.

#### Status

```
status
```

This will check the status of a given address. If no address is provided, it will check your own status.

The status includes your account balance on the exchange (in dollars), the amount of Hackcoin you own, and the current market price of Hackcoin.

Your hackcoin balance is computed with respect to the current valid and active chain.

#### View Blockchain

```
bc
```

This will print out the current blockchain in a table format. The information is the same displayed on our website visualizer

### Who

```
who
```

This will print the other known hackcoin nodes on the network, along with their public address

#### Transfer

```
transfer <receiver> <amount>
```

This will transfer `<amount>` hackcoin to the address provided in `<receiver>`. The transaction will appear once someone has mined a new block.

#### Transactions

```
txns
```

This prints out the current pending transactions. Pending transactions are transactions that are waiting to be added to the blockchain once somebody mines a block.

#### Buy Hackcoin

```
buy <amount>
```

This allows you to buy `<amount>` of hackcoin from the user named `vendor` at the market price. The transaction will be added to the blockchain on the next mined block

#### Sell Hackcoin

```
sell <amount>
```

This allows you to sell `<amount>` of hackcoin to the user named `vendor` at the market price. The vendor requires you to publish the transaction to transfer `<amount>` of hackcoin to the list of pending transactions so they can verify the payment before sending the money.

#### Donate

```
donate
```

This allows you to donate to the Hackbase corporation. Donations are only made in amounts of $1,333,337

## Tips

The puzzle resets every 2 hours :). Your solution should not require this much time to run

<!-- ## Donate

HackCoin is a valid cryptocurrency. If you're feeling generous and liked this puzzle, you can donate a few blockchains our way,

```
df55754943142026092a8f5ecc768950ab09becd95a4f65cd7516618957b65b9
```

(Wait for us to announce the tracker to discover valid peers after the puzzle is over.) -->
