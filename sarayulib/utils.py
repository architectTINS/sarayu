"""Utilities"""

import os
import logging
import re
import subprocess

from starkware.starknet.public.abi import get_selector_from_name

GATEWAY={"localhost": "http://127.0.0.1:5050/"}

def set_network_var(network="localhost"):
    if network == "mainnet":
        os.environ["STARKNET_NETWORK"] = "alpha-mainnet"
        return True
    elif network == "goerli":
        os.environ["STARKNET_NETWORK"] = "alpha-goerli"
        return True

    return

def get_account_file_name(network):
    return f"{network}.accounts.json"

# Taken from nile.
def str_to_felt(text):
    """Return a field element from a given string."""
    b_text = bytes(text, "ascii")
    return int.from_bytes(b_text, "big")


def is_string(param):
    """Identify a param as string if is not int or hex."""
    is_int = True
    is_hex = True

    # convert to integer
    try:
        int(param)
    except Exception:
        is_int = False

    # convert to hex (starting with 0x)
    try:
        assert param.startswith("0x")
        int(param, 16)
    except Exception:
        is_hex = False

    return not is_int and not is_hex


def normalize_number(number):
    """Normalize hex or int to int."""
    if type(number) == str and number.startswith("0x"):
        return int(number, 16)
    else:
        return int(number)


def hex_address(number):
    """Return the 64 hexadecimal characters length address."""
    if type(number) == str and number.startswith("0x"):
        return _pad_hex_to_64(number)
    else:
        return _pad_hex_to_64(hex(int(number)))


def _pad_hex_to_64(hexadecimal):
    if len(hexadecimal) < 66:
        missing_zeros = 66 - len(hexadecimal)
        return hexadecimal[:2] + missing_zeros * "0" + hexadecimal[2:]


def stringify(x, process_short_strings=False):
    """Recursively convert list or tuple elements to strings."""
    if isinstance(x, list) or isinstance(x, tuple):
        return [stringify(y, process_short_strings) for y in x]
    else:
        if process_short_strings and is_string(x):
            return str(str_to_felt(x))
        return str(x)


def parse_information(x):
    """Extract information from deploy/declare command."""
    # address is 64, tx_hash is 64 chars long
    address, tx_hash = re.findall("0x[\\da-f]{1,64}", str(x))
    return normalize_number(address), normalize_number(tx_hash)


def deployment_exists(address_or_alias, network="localhost"):
    """
    Return whether a deployment exists or not.
    - If address_or_alias is an int, address is assumed.
    - If address_or_alias is a str, alias is assumed.
    """
    deployment = next(deployments_load(address_or_alias, network), None)
    return deployment is not None


def deployments_load(address_or_alias, network="localhost"):
    """
    Load deployments that matches an identifier (address or alias).
    - If address_or_alias is an int, address is assumed.
    - If address_or_alias is a str, alias is assumed.
    """
    file = f"{network}.deployments.txt"
    if not os.path.exists(file):
        return

    with open(file) as fp:
        for line in fp:
            [address, abi, *alias] = line.strip().split(":")
            address = normalize_number(address)
            identifiers = [address]
            if type(address_or_alias) is not int:
                identifiers = alias
            if address_or_alias in identifiers:
                yield address, abi

def deployments_register(address, abi, network, alias):
    """Register a new deployment."""
    file = f"{network}.deployments.txt"

    if alias is not None:
        if deployment_exists(alias, network):
            raise Exception(f"Alias {alias} already exists in {file}")

    with open(file, "a") as fp:
        # Save address as hex
        address = hex_address(address)
        if alias is not None:
            logging.info(f"📦 Registering deployment as {alias} in {file}")
        else:
            logging.info(f"📦 Registering {address} in {file}")

        fp.write(f"{address}:{abi}")
        if alias is not None:
            fp.write(f":{alias}")
        fp.write("\n")

def from_call_to_call_array(calls):
    """Transform from Call to CallArray."""
    call_array = []
    calldata = []
    for _, call in enumerate(calls):
        assert len(call) == 3, "Invalid call parameters"
        entry = (
            call[0],
            get_selector_from_name(call[1]),
            len(calldata),
            len(call[2]),
        )
        call_array.append(entry)
        calldata.extend(call[2])
    return (call_array, calldata)

def parse_send(x):
    """Extract information from send command."""
    # address is 64, tx_hash is 64 chars long
    try:
        address, tx_hash = re.findall("0x[\\da-f]{1,64}", str(x))
        return address, tx_hash
    except ValueError:
        print(f"could not get tx_hash from message {x}")
    return 0x0, 0x0
