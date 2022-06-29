from itertools import chain
from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv
load_dotenv()
with open("./SimpleStorage.sol") as file:
    simple_storage_file = file.read()
install_solc("0.6.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)
with open("compiled_coded.json", "w") as file:
    json.dump(compiled_sol, file)


bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1337
my_address = "0x9777F1486c5D414f158e400d2E12FA8cB71cF00D"
private_key = os.getenv("PRIVATE_KEY")

SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

nonce = w3.eth.getTransactionCount(my_address)

transaction = SimpleStorage.constructor().buildTransaction({
    "gasPrice": w3.eth.gas_price,
    "chainId": chain_id,
    "from": my_address,
    "nonce": nonce,
})

signed_txn = w3.eth.account.sign_transaction(transaction, private_key= private_key)

tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print(simple_storage.functions.retrieve().call())
store_transaction =  simple_storage.functions.store(15).buildTransaction(
    {"chainId" : chain_id, "from": my_address, "nonce": nonce + 1}
)

signed_stored_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key)

send_store_tx = w3.eth.send_raw_transaction(signed_stored_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt()