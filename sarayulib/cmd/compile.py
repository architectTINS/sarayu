#!./bin/python

import sys
import logging
import subprocess
import os

from sarayulib.constants import OUTPUT_DIR, ABIS_DIR, CONTRACTS_DIR

logging.basicConfig(level=logging.INFO, format="%(message)s")

def get_all_contracts(directory=None):
    """Get all cairo contracts in the default contract directory."""

    ext = ".cairo"
    files = list()
    for (dirpath, _, filenames) in os.walk(directory if directory else CONTRACTS_DIR):
        files += [ os.path.join(dirpath, file) for file in filenames if file.endswith(ext) ]
    return files

def compile_contracts(contracts, directory=None):
    """Compile cairo contracts."""

    contracts_dir = directory if directory else CONTRACTS_DIR

    if not os.path.exists(OUTPUT_DIR):
        logging.info(f"📁 Creating {OUTPUT_DIR} to store output json files")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not os.path.exists(ABIS_DIR):
        logging.info(f"📁 Creating {ABIS_DIR} to store compilation artifacts")
        os.makedirs(ABIS_DIR, exist_ok=True)

    all_contracts = contracts

    if len(contracts) == 0:
        logging.info( f"🤖 Compiling all Cairo contracts in the {contracts_dir} directory" )
        all_contracts = get_all_contracts(directory=contracts_dir)

    results = [ _compile_contract(contract, contracts_dir) for contract in all_contracts ]
    failed_contracts = [c for (c, r) in zip(all_contracts, results) if r != 0]
    failures = len(failed_contracts)

    if failures == 0:
        logging.info("✅ Done")
    else:
        exp = f"{failures} contract"
        if failures > 1:
            exp += "s"  # pluralize
        logging.info(f"🛑 Failed to compile the following {exp}:")
        for contract in failed_contracts:
            logging.info(f"   {contract}")

def _compile_contract(path, directory=None):
    base = os.path.basename(path)
    filename = os.path.splitext(base)[0]
    logging.info(f"🔨 Compiling {path}")
    contracts_dir = directory if directory else CONTRACTS_DIR

    cmd = f"""starknet-compile {path} --cairo_path={contracts_dir} --output {OUTPUT_DIR}/{filename}.json --abi {ABIS_DIR}/{filename}.json"""

    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    process.communicate()
    return process.returncode



if __name__ == "__main__":
    args = sys.argv
    logging.debug(f"Length of arguments = {len(args)}")
    if len(args) > 1:
        logging.debug(f"Arguments = {args}")
        logging.debug(f"args[1:]  = {args[1:]}")
        compile_contracts((args[1:]))
        #compile(('contracts/game.cairo',))
    else:
        compile_contracts(())
