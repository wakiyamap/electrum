#!/usr/bin/env bash
export HOME=~
set -eux pipefail
mkdir -p ~/.monacoin
cat > ~/.monacoin/monacoin.conf <<EOF
regtest=1
txindex=1
printtoconsole=1
rpcuser=doggman
rpcpassword=donkey
rpcallowip=127.0.0.1
zmqpubrawblock=tcp://127.0.0.1:28332
zmqpubrawtx=tcp://127.0.0.1:28333
fallbackfee=0.0002
[regtest]
rpcbind=0.0.0.0
rpcport=19443
EOF
rm -rf ~/.monacoin/regtest
screen -S monacoind -X quit || true
screen -S monacoind -m -d monacoind -regtest
sleep 6
# bitcoin-cli createwallet test_wallet
addr=$(monacoin-cli getnewaddress)
monacoin-cli generatetoaddress 150 $addr > /dev/null
