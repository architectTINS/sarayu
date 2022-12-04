import logging
import subprocess
import json

from sarayulib.utils import (
    set_network_var,
    GATEWAY
)

def get_tx_status(tx_hash: str, network="localhost"):
    """Returns transaction receipt in dict."""

    command = ["starknet", "tx_status", "--hash", tx_hash]
    
    if set_network_var(network) is None:
        command.append(f"--feeder_gateway_url={GATEWAY.get(network)}")

    logging.debug("⏳ Querying the network to check transaction status and identify contracts...")
    logging.debug(command)
    
    out = subprocess.check_output(command)
    receipt = json.loads(out)
    logging.debug(f"TX_STATUS: {receipt}")
    return receipt["tx_status"]
