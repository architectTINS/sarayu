#!./bin/python

import os
import json
import logging
import subprocess

from sarayulib.utils import (
    GATEWAY, 
    deployments_register, hex_address,
    get_account_file_name,
    normalize_number, parse_information,
    set_network_var
    )
from starkware.crypto.signature.signature import private_to_stark_key

logging.basicConfig(level=logging.INFO, format="%(message)s")

def account_exists(pubkey, network):
    """Return whether an account exists or not."""
    account = next(account_load(pubkey, network), None)
    return account is not None


def account_load(pubkey, network):
    """Load account that matches a pubkey."""
    file = get_account_file_name(network)

    if not os.path.exists(file):
        with open(file, "w") as fp:
            json.dump({}, fp)

    with open(file) as fp:
        accounts = json.load(fp)
        # pubkey in file is in hex format
        pubkey = hex(pubkey)
        if pubkey in accounts:
            accounts[pubkey]["address"] = normalize_number(accounts[pubkey]["address"])
            yield accounts[pubkey]


def current_index(network):
    """Return the length of the accounts. Used as the next index."""
    file = get_account_file_name(network)

    with open(file) as fp:
        accounts = json.load(fp)
        return len(accounts.keys())

def accounts_register(pubkey, address, index, alias, network):
    """Register a new account."""
    file = get_account_file_name(network)

    if account_exists(pubkey, network):
        raise Exception(f"account-{index} already exists in {file}")

    with open(file, "r") as fp:
        accounts = json.load(fp)
        # Save public key as hex
        pubkey = hex(pubkey)
        accounts[pubkey] = {
            "address": hex_address(address),
            "index": index,
            "alias": alias,
        }
    with open(file, "w") as file:
        json.dump(accounts, file)


def account_setup(private_key, network="localhost"):
    "Deploy an account contract"
    try:
        public_key = private_to_stark_key(normalize_number(os.environ[private_key]))
        #print("private: ", os.environ[private_key])
        #print("public:  ", public_key)
        #print("private: ", hex_address(os.environ[private_key]))
        #print("public:  ", hex_address(public_key))

    except KeyError:
        logging.error(f"\n❌ Cannot find {private_key} in env.\nCheck spelling and that it exists.\nTry moving the .env to the root of your project.")
        return
    
    abi_path = os.path.dirname(os.path.realpath(__file__)).replace("/cmd", "/artifacts/account_abi.json")
    contract_path = os.path.dirname(os.path.realpath(__file__)).replace("/cmd", "/artifacts/account_contract.json")

    if not account_exists(public_key,network):
        index = current_index(network)
        logging.info(f"🚀 Deploying Account")
        command = ["starknet", "deploy", "--contract", contract_path, "--inputs", f"{public_key}"]

        if set_network_var(network) is None:
            command.append(f"--gateway_url={GATEWAY.get(network)}")

        command.append("--no_wallet")

        logging.info(command)

        #print(command)
        output = subprocess.check_output(command)

        address, tx_hash = parse_information(output)

        logging.info(f"⏳ ️Deployment of Account successfully sent at {hex_address(address)}")
        logging.info(f"🧾 Transaction hash: {hex(tx_hash)}")

        deployments_register(address, abi_path, network, f"account-{index}")
        accounts_register(public_key, address, index, private_key, network)

    else:
        print("Account exists...")


if __name__ == "__main__":
    account_setup('STARKNET_PRIVATE_KEY')