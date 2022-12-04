# SARAYU
A tool to interact with starknet contracts.
Inspired and forked from [nile](https://github.com/OpenZeppelin/nile).

By default, the environment variable is set STARKNET_LOCAL_NET=1 in every new shell launched.
This will cause all the commands to be invoked on the devnet.

To use mainnet or goerli, unset this variable in each terminal.

Installation:
This repo needs to be cloned to ~/cario/tools/sarayu
- mkdir -p ~/cairo/tools/sarayu
- cd ~/cairo/tools/sarayu
- git clone https://github.com/architectTINS/sarayu .

Usage:
1. Execute ~/cairo/tools/sarayu/sarayuinit.sh in a fresh cloned venv workspace.
   - This adds path setting commands in bin/activate
2. Activate the workspace.

