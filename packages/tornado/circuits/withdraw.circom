pragma circom 2.0.0;

include "../../../node_modules/circomlib/circuits/poseidon.circom";
include "../../../node_modules/circomlib/circuits/bitify.circom";
include "merkleTree.circom";

template Withdraw(levels) {
  signal input root;
  signal input nullifierHash;
  signal input recipient;
  signal input relayer;
  signal input fee;
  signal input nullifier;
  signal input pathElements[levels];
  signal input pathIndices[levels];

  component leafIndexNum = Bits2Num(levels)
  for (var i = 0; i < levels; i++) {
    leafIndexNum.in[i] <== pathIndices[i];
  }

  component nullifierHasher = Poseidon(3);
  nullifierHasher.inputs[0] <== nullifier;
  nullifierHasher.inputs[1] <== 1;
  nullifierHasher.inputs[2] <== leafIndexNum.out;
  nullifierHasher.out === nullifierHash;

  component commitmentHasher = Poseidon(2);
  commitmentHasher.inputs[0] <== nullifier;
  commitmentHasher.inputs[1] <== 0;

  component tree = MerkleProofValidator(levels);
  tree.leaf <== commitmentHasher.out;
  tree.root <== root

  for (var i = 0; i < levels; i++) {
    tree.pathElements[i] <== pathElements[i];
    tree.pathIndices[i] <== pathIndices[i];
  }

  signal recipientSquare;
  signal feeSquare;
  signal relayerSquare;

  recipientSquare <== recipient * recipient
  feeSquare <== fee * fee
  relayerSquare <== relayer * relayer
}

component main {public [root, nullifierHash, recipient, relayer, fee]} = Withdraw(20);