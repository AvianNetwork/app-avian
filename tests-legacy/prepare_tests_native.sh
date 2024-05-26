#!/bin/bash
bash ./clean_tests.sh

# TODO: tests currently not working with DEBUG=1

cd ..
make clean
make -j DEBUG=0 COIN=avian_testnet
mv bin/ tests-legacy/avian-testnet-bin
