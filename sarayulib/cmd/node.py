"""Command to start StarkNet local network."""
import subprocess
import logging

def node(host="127.0.0.1", port=5050, seed=None):
    try:
        command = ["starknet-devnet", "--host", host, "--port", str(port)]

        if seed is not None:
            command.append("--seed")
            command.append(str(seed))

        subprocess.check_call(command)
    except FileNotFoundError:
        logging.error(
            "\n\n😰 Could not fine starknet-devnet. Install it with:\n"
            "    pip install starknet-devnet")