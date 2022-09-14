pragma circom 2.0.0;

include "../../../node_modules/circomlib/circuits/poseidon.circom";

// if s == 0 return in[0], in[1]
// if s == 1 return in[1], in[0]
template DaulMux() {
  signal input in[2];
  signal input s;
  signal output out[2];
  s * (1 - s) === 0;
  out[0] <== (in[1] - in[0])*s + in[0];
  out[1] <== (in[0] - in[1])*s + in[1];
}