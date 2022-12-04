
# execute this from the workspace after creating a virtual environment
# from the parent folder of the bin folder.

# These are to run the scripts standalone
echo 'export PYTHONPATH="${PYTHONPATH:+"$PYTHONPATH:"}${PWD}/libext"' >> bin/activate
echo 'export PYTHONPATH="${PYTHONPATH:+"$PYTHONPATH:"}${HOME}/cairo/tools/sarayu"' >> bin/activate

echo '\nPATH="$PATH":$HOME/cairo/tools/sarayu' >> bin/activate
echo 'export PATH' >> bin/activate
echo "export STARKNET_LOCAL_NET=1" >> bin/activate

echo "/home/bharathishri/cairo/tools/sarayu" > lib/python3.9/site-packages/virt.pth



