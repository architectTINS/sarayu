#!./bin/python

import logging
import subprocess
import os

from sarayulib.utils import (
    GATEWAY,
    is_string, normalize_number, hex_address,
    deployments_load, set_network_var,
    stringify
)

logging.basicConfig(level=logging.INFO, format="%(message)s")

def call_function(address_or_alias, view_function, params=[], network="localhost"):
    if not is_string(address_or_alias):
        address_or_alias = normalize_number(address_or_alias)

    address, abi = next(deployments_load(address_or_alias, network))
    #print(hex_address(address))

    command = ["starknet", "call", "--address", hex_address(address), "--abi", abi, "--function", view_function]

    if params is None:
        params = []
    params = stringify(params, True)

    if len(params) > 0:
        command.append("--inputs")
        command.extend(params)

    if set_network_var(network) is None:
        command.append(f"--feeder_gateway_url={GATEWAY.get(network)}")
        command.append(f"--gateway_url={GATEWAY.get(network)}")

    command.append("--no_wallet")

    logging.debug(command)

    try:
        out = subprocess.check_output(command).strip().decode("utf-8")
    except subprocess.CalledProcessError:
        p = subprocess.Popen(command, stderr=subprocess.PIPE)
        _, error = p.communicate()
        err_msg = error.decode()

        if "max_fee must be bigger than 0" in err_msg:
            logging.error("""\n😰 Whoops, looks like max fee is missing. Try with:\n
                          --max_fee=`MAX_FEE`""")
        elif "transactions should go through the __execute__ entrypoint." in err_msg:
            logging.error("\n\n😰 Whoops, looks like you're not using an account. Try with:\n"
                          "\nnile send [OPTIONS] SIGNER CONTRACT_NAME METHOD [PARAMS]")
        
        out=''
    
    #print(out)
    return out

if __name__ == "__main__":
    call_function("balance", "get_balance")