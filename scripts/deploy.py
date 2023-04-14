from starknet_py.common import create_casm_class
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.net.udc_deployer.deployer import Deployer
import asyncio
import subprocess
import os
from accounts import get_account

account = get_account()
MAX_FEE=int(1e16)


def compile_contract(cairo_file_path: str):
    """
    Compile the cairo file to json file with starknet-compile
    Save the json file to src/build
    Compile the json file to casm file with starknet-sierra-compile
    """
    # create the build folder if not exist
    if not os.path.exists('src/build'):
        os.makedirs('src/build')
    
    # compile the cairo file, save to json file
    json_file_path = os.path.join('src/build/', os.path.basename(cairo_file_path).split('.')[0] + '.json') # get the json file path
    subprocess.call(['starknet-compile', cairo_file_path, json_file_path])
    with open(json_file_path, 'r') as f:
        compiled_contract = f.read()
    
    # compile the json file, save to casm file
    casm_file_path = os.path.join('src/build/', os.path.basename(cairo_file_path).split('.')[0] + '.casm') # get the casm file path
    subprocess.call(['starknet-sierra-compile', json_file_path, casm_file_path, '--add-pythonic-hints'])
    # compiled_contract_casm = subprocess.getstatusoutput('starknet-sierra-compile src/hello_starknet.json --add-pythonic-hints')[1] # use this if you dont want to save the casm file
    with open(casm_file_path, 'r') as f:
        compiled_contract_casm = f.read()
    return compiled_contract, compiled_contract_casm

async def declare_contract(compiled_contract, compiled_contract_casm):
    # contract_compiled_casm is the output of the starknet-sierra-compile (.casm file)
    casm_class = create_casm_class(compiled_contract_casm)

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
    return sierra_class_hash


async def deploy_contract(compiled_contract=0, compiled_contract_casm=0):
    # Use Universal Deployer Contract (UDC) to deploy the Cairo1 contract
    deployer = Deployer()

    # sierra_class_hash = await declare_contract(compiled_contract, compiled_contract_casm)
    sierra_class_hash = '0x3ae6bb224f12a8818c3ad59cc248968e8ee3a3081ff805610141695381a28f7' # use class_hash directly if contract is already declared

    # Create a ContractDeployment, optionally passing salt and raw_calldata
    contract_deployment = deployer.create_contract_deployment_raw(
        class_hash=sierra_class_hash
    )

    # Using the call, create an Invoke transaction to the UDC
    deploy_invoke_transaction = await account.sign_invoke_transaction(
        calls=contract_deployment.call, max_fee=MAX_FEE
    )
    resp = await account.client.send_transaction(deploy_invoke_transaction)
    print(resp.transaction_hash)

def main():
    # compiled_contract, compiled_contract_casm = compile_contract('src/hello_starknet.cairo')
    # asyncio.run(declare_contract(compiled_contract = compiled_contract, compiled_contract_casm=compiled_contract_casm))
    asyncio.run(deploy_contract())

if __name__ == "__main__":
    main()