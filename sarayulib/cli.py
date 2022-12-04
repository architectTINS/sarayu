#!/usr/bin/env python
""" sarayu CLI entry point """
import logging
import click
import os
import sarayulib.constants as consts
from sarayulib.cmd.setup import account_setup
from sarayulib.cmd.node import node as node_cmd
from sarayulib.cmd.compile import compile_contracts as compile_cmd
from sarayulib.cmd.deploy import deploy_contract as deploy_cmd
from sarayulib.cmd.call import call_function as call_cmd
from sarayulib.cmd.invoke import invoke_function as invoke_cmd
from sarayulib.cmd.tx_status import get_tx_status as txstatus_cmd

logging.basicConfig(level=logging.INFO, format="%(message)s")

def network_option(f):
  """Configure NETWORK option for the cli."""
  
  net_type = "STARKNET_NETWORK" if os.environ.get('STARKNET_LOCAL_NET') is None else ""

  return click.option(
    "--network",
    envvar=net_type,
    default="localhost", 
    help=f"Select network, one of {consts.NETWORKS}",
    callback=_validate_network
    )(f)

def _validate_network(_ctx, _param, value):
    """Normalize network values."""
    # normalize goerli
    if "goerli" in value or "testnet" in value:
        return "goerli"
    # normalize localhost
    if "localhost" in value or "127.0.0.1" in value:
        return "localhost"
    # check if value is accepted
    if value in consts.NETWORKS:
        return value
    # raise if value is invalid
    raise click.BadParameter(f"'{value}'. Use one of {consts.NETWORKS}")


@click.group()
def cli():
    """
    sarayu CLI group.
    """
    pass

@cli.command()
@click.option("--pkey", default="STARKNET_PRIVATE_KEY")
@network_option
def setup(pkey, network):
    """Deploy an account contract\n
    
    syntax:\n
      sarayu setup --pkey "STARKNET_PRIVATE_KEY" --network "localhost"

    """
    account_setup(pkey, network)

@cli.command()
@click.argument("contracts", nargs=-1)
@click.option("--directory")
def compile(contracts, directory):
  """
  Compile the contracts.
  """
  compile_cmd(contracts, directory)

@cli.command()
@click.option("--host", default="127.0.0.1")
@click.option("--port", default=5050)
@click.option("--seed", default=int)
def node(host, port, seed):
    """
    Start Starknet local network\n
    
    $ sarayu node
      : Start StarkNet local network at port 5050

    $ sarayu node --host HOST --port 5001
      : Start StarkNet local network on address HOST listening at port 5001

    $ sarayu node --seed SEED
      : Start StarkNet local network with seed SEED
    
    Direct StarkNet command:\n
      starknet-devnet --host localhost -p 5050 --seed 1001
    """
    node_cmd(host, port, seed)

@cli.command()
@click.argument("contract_name", nargs=1)
@click.option("--alias")
@network_option
def deploy(contract_name, alias, network):
  """
  Deploy a StarkNet contract.
  """
  deploy_cmd(contract_name,alias,network)

@cli.command()
@click.argument("address_or_alias", nargs=1)
@click.argument("view_function", nargs=1)
@click.argument("params", nargs=-1)
@network_option
def call(address_or_alias, view_function, params, network):
  """Call functions of StarkNet contracts."""
  out = call_cmd(address_or_alias, view_function, params, network)
  print(out)

@cli.command()
@click.argument("contract_alias", nargs=1)
@click.argument("invoke_function", nargs=1)
@click.argument("arguments", nargs=-1)
@click.option("--pkey", default="STARKNET_PRIVATE_KEY")
@network_option
def invoke(contract_alias, invoke_function, arguments, pkey, network):
  """
  Invoke a StarkNet contract.
  
  """
  logging.debug("arguments list: ", arguments)
  out = invoke_cmd(contract_alias, invoke_function, arguments, pkey, network)
  print(out)

@cli.command()
@click.argument("tx_hash", nargs=1)
@network_option
def txstatus(tx_hash,network):
  """
  Get TX_STATUS info for a transaction hash.

  Direct StarkNet command:\n
    $ starknet tx_status --hash <hash beginning with 0x> --feeder_gateway_url=http://127.0.0.1:5050/
  """
  out = txstatus_cmd(tx_hash,network)

@cli.command()
def setlocal():
  """
  Write "export STARKNET_LOCAL_NET=1" into bin/activate.
  If this variable is set, then STARKNET_NETWORK is overriden, and devnet is used instead.
  """
  with open("bin/activate", "a") as fp:
    fp.write(f"export STARKNET_LOCAL_NET=1")
    fp.write("\n")
    
  print("STARKNET_LOCAL_NET set to 1. Please run a new shell")
