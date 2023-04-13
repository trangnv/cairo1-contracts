from starknet_py.common import create_casm_class
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from accounts import get_account
import asyncio
import subprocess

account = get_account()
MAX_FEE=int(1e16)

async def declare_contract(contract_compiled_casm, compiled_contract):
    # contract_compiled_casm is the output of the starknet-sierra-compile (.casm file)
    casm_class = create_casm_class(contract_compiled_casm)

    # Compute Casm class hash
    casm_class_hash = compute_casm_class_hash(casm_class)

    # Create Declare v2 transaction
    declare_v2_transaction = await account.sign_declare_v2_transaction(
        # compiled_contract is the output of the starknet-compile (.json file)
        compiled_contract=compiled_contract,
        compiled_class_hash=casm_class_hash,
        max_fee=MAX_FEE,
    )

    # Send Declare v2 transaction
    resp = await account.client.declare(transaction=declare_v2_transaction)
    await account.client.wait_for_tx(resp.transaction_hash)

    sierra_class_hash = resp.class_hash
    print(sierra_class_hash)

def main():
    # starknet-compile and save to json file
    subprocess.call(['starknet-compile', 'src/hello_starknet.cairo', 'src/hello_starknet.json'])
    ## read the json file
    with open('src/hello_starknet.json', 'r') as f:
        compiled_contract = f.read()

    # starknet-sierra-compile, dont need to save 
    contract_compiled_casm = subprocess.getstatusoutput('starknet-sierra-compile src/hello_starknet.json --add-pythonic-hints')[1]
    asyncio.run(declare_contract(contract_compiled_casm, compiled_contract))

if __name__ == "__main__":
    main()