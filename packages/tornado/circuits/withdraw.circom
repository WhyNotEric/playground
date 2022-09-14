pragma circom 2.0.0;

include "../../../node_modules/circomlib/circuits/poseidon.circom";
include "../../../node_modules/circomlib/circuits/bitify.circom";
include "merkleTree.circom";

template Multiplier2() {
  signal input a;
  signal input b;
  signal output c;
  c <== a * b;
}

component main = Multiplier2();