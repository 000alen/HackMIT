from web3 import Web3
from solcx import compile_source

CONTRACT_ADDRESS = "0x98CD3B326E1248061d684Ae230F580b74195dD86"
PROVIDER_URL = "https://ropsten.infura.io/v3/ad31d30c3c96492d9a7fc9324f4ddfde"
SOURCE = open("contract.sol").read()

compiled_sol = compile_source(SOURCE)
contract_id, contract_interface = compiled_sol.popitem()
abi = contract_interface["abi"]
w3 = Web3(Web3.HTTPProvider(PROVIDER_URL))
contract = w3.eth.contract(CONTRACT_ADDRESS, abi=abi)

print(f"Board: {contract.functions.getBoard().call()}")
print(f"Moves: {contract.functions.getMoves().call()}")
print(f"Lives: {contract.functions.getLives().call()}")
print(f"Player Pos: {contract.functions.getPlayerPos().call()}")
