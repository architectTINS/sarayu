#!./bin/python

import logging
import subprocess
import os

from sarayulib.utils import (
    GATEWAY,
    hex_address, parse_information,
    deployments_register,
    set_network_var
    )

from sarayulib.constants import OUTPUT_DIR, ABIS_DIR, CONTRACTS_DIR

logging.basicConfig(level=logging.INFO, format="%(message)s")

def deploy_contract(contract_name, alias=None, network="localhost"):
    """Deploy StarkNet smart contracts."""
    logging.info(f"🚀 Deploying {contract_name}")

    command = ["starknet", "deploy", "--contract", f"{OUTPUT_DIR}/{contract_name}.json"]


    if set_network_var(network) is None:
        command.append(f"--gateway_url={GATEWAY.get(network)}")

    command.append("--no_wallet")
    logging.info(command)

    output = subprocess.check_output(command)

    address, tx_hash = parse_information(output)
    logging.info(f"⏳ ️Deployment of {contract_name} successfully sent at {hex_address(address)}")
    logging.info(f"🧾 Transaction hash: {hex(tx_hash)}")

    deployments_register(address,
                        f"{ABIS_DIR}/{contract_name}.json",
                        network,
                        alias if alias else contract_name)
    return address


if __name__ == "__main__":
    #deploy_contract(('102-balance'))
    deploy_contract(('102-balance'), alias="balance", network="localhost")
