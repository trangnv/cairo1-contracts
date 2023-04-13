from starknet_py.net.account.account import Account
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
import os
from dotenv import load_dotenv
load_dotenv()

network = "testnet"
def get_account():
    client = GatewayClient(net=network)
    account_address = os.getenv('ACCOUNT_ADDRESS')
    private_key = int(os.getenv('PRIVATE_KEY'),16) # PRIVATE_KEY is hex in .env file
    key_pair = KeyPair.from_private_key(key=private_key)

    signer = StarkCurveSigner(account_address, key_pair, StarknetChainId.TESTNET)

    account = Account(client=client, address=account_address, signer=signer)
    return account