from starknet_py.common import create_casm_class
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from accounts import get_account
import asyncio

account = get_account()
MAX_FEE=int(1e16)

async def declare_contract(contract_compiled_casm_file, compiled_contract_file):
    # contract_compiled_casm is the output of the starknet-sierra-compile (.casm file)
    casm_class = create_casm_class(contract_compiled_casm_file)

    # Compute Casm class hash
    casm_class_hash = compute_casm_class_hash(casm_class)

    # Create Declare v2 transaction
    declare_v2_transaction = await account.sign_declare_v2_transaction(
        # compiled_contract is the output of the starknet-compile (.json file)
        compiled_contract=compiled_contract_file,
        compiled_class_hash=casm_class_hash,
        max_fee=MAX_FEE,
    )

    # Send Declare v2 transaction
    resp = await account.client.declare(transaction=declare_v2_transaction)
    await account.client.wait_for_tx(resp.transaction_hash)

    sierra_class_hash = resp.class_hash

def main():
    print(hex(account.address))

if __name__ == "__main__":
    main()