#!./bin/python

import logging
import subprocess
import os

from starkware.crypto.signature.signature import private_to_stark_key, sign
from sarayulib.cmd.setup import account_exists, account_load
from starkware.starknet.core.os.transaction_hash.transaction_hash import TransactionHashPrefix, calculate_transaction_hash_common
from starkware.starknet.definitions.general_config import StarknetChainId

from sarayulib.utils import (
    GATEWAY,
    is_string, normalize_number, hex_address,
    deployments_load,
    from_call_to_call_array,
    stringify,
    parse_send,
    set_network_var,
)
from sarayulib.cmd.tx_status import get_tx_status
from sarayulib.constants import MAX_FEE, TRANSACTION_VERSION

logging.basicConfig(level=logging.INFO, format="%(message)s")

def get_nonce(contract_address, network="localhost"):
    """Get the current nonce."""
    # Starknet CLI requires a hex string for get_nonce command
    if not str(contract_address).startswith("0x"):
        contract_address = hex(int(contract_address))

    command = ["starknet", "get_nonce", "--contract_address", contract_address]

    if network == "mainnet":
        os.environ["STARKNET_NETWORK"] = "alpha-mainnet"
    elif network == "goerli":
        os.environ["STARKNET_NETWORK"] = "alpha-goerli"
    else:
        command.append(f"--feeder_gateway_url={GATEWAY.get(network)}")

    logging.debug(command)

    return int(subprocess.check_output(command).strip())

def invoke_function(contract_alias, invoke_function, arguments, pkey="STARKNET_PRIVATE_KEY", network="localhost"):
    ## out = send(network, signer_alias, contract_alias, function, arguments)

    if not isinstance(arguments[0], list):
        arguments = [arguments]

    target_address, _ = next(deployments_load(contract_alias, network)) or contract_alias
    calldata = [[int(x) for x in c] for c in arguments]

    priv_key = normalize_number(os.environ[pkey])
    public_key = private_to_stark_key(priv_key)

    if account_exists(public_key, network):
        data = next(account_load(public_key, network))
        logging.debug("account exists: ", data)
        address = data["address"]
    else:
        logging.error("Account not deployed.")
        return

    nonce = get_nonce(address, network)
    logging.debug("nonce=", nonce)
    
    calls = [[target_address, invoke_function, c] for c in calldata]
    call_array, calldata = from_call_to_call_array(calls)

    execute_calldata = [len(call_array), *[x for t in call_array for x in t],
                        len(calldata), *calldata,]

    if isinstance(address, str):
        sender = int(address, 16)
    else:
        sender = address

    transaction_hash = calculate_transaction_hash_common(
        tx_hash_prefix=TransactionHashPrefix.INVOKE,
        version=TRANSACTION_VERSION,
        contract_address=sender,
        entry_point_selector=0,
        calldata=execute_calldata,
        max_fee=MAX_FEE,
        chain_id=StarknetChainId.TESTNET.value,
        additional_data=[nonce]
    )

    sig_r, sig_s = sign(transaction_hash, priv_key)
    signature = [str(sig_r), str(sig_s)]

    address, abi = next(deployments_load(address,network))
    address = hex_address(address)

    if execute_calldata is None:
        execute_calldata = []
    params = stringify(execute_calldata, True)

    command = ["starknet", "invoke", "--address", address, "--abi", abi, "--function", "__execute__", ]

    if set_network_var(network) is None:
        command.append(f"--feeder_gateway_url={GATEWAY.get(network)}")
        command.append(f"--gateway_url={GATEWAY.get(network)}")

    if len(params) > 0:
        command.append("--inputs")
        command.extend(params)

    if signature is not None:
        command.append("--signature")
        command.extend(signature)

    command.append("--max_fee")
    command.append(str(MAX_FEE))

    command.append("--no_wallet")
    logging.debug(command)

    try:
        out = subprocess.check_output(command).strip().decode("utf-8")
    except subprocess.CalledProcessError:
        p = subprocess.Popen(command, stderr=subprocess.PIPE)
        _, error = p.communicate()
        err_msg = error.decode()

        if "max_fee must be bigger than 0" in err_msg:
            logging.error("""\n😰 Whoops, looks like max fee is missing. Try with:\n--max_fee=`MAX_FEE`""")
        elif "transactions should go through the __execute__ entrypoint." in err_msg:
            logging.error(
                "\n\n😰 Whoops, looks like you're not using an account. Try with:\n"
                "\nnile send [OPTIONS] SIGNER CONTRACT_NAME METHOD [PARAMS]"
            )

        out =''

    logging.info(out)
    
    if(out):
        _, tx_hash = parse_send(out)
        out = get_tx_status(tx_hash, network)

    return out
    
if __name__ == "__main__":
    #invoke_function("balance", "increase_balance", [220], pkey='STARKNET_PRIVATE_KEY',)

    from starknet_wrapper import wrapped_send
    from constants import NETWORK
    import logging

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    wrapped_send(NETWORK, "STARKNET_PRIVATE_KEY", "balance", "increase_balance", [100])
