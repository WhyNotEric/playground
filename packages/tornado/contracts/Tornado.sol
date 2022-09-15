// SPDX-License-Identifier: GPL-3.0-only

pragma solidity 0.8.9;

import "./MerkleTreeWithHistory.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

struct Proof {
  uint256[2] a;
  uint256[2][2] b;
  uint256[2] c;
}

interface IVerifier {
  function verifyProof(
    uint256[2] calldata a,
    uint256[2][2] calldata b,
    uint256[2] calldata c,
    uint256[5] calldata input) 
    external view returns (bool);
}

abstract contract Tornado is MerkleTreeWithHistory, ReentrancyGuard {
  uint256 public immutable denomination;
  IVerifier public immutable verifier;

  mapping(bytes32 => bool) public nullifierHashes;

  event Deposit(bytes32 indexed commitment, uint32 leafIndex, uint256 timestamp);
  event Withdraw(address to, bytes32 nullifierHash, address indexed replayer, uint256 fee);

  constructor(
    IVerifier _verifier,
    uint256 _denomination,
    uint32 _merkleTreeHeight,
    address _hasher)
    MerkleTreeWithHistory(_merkleTreeHeight, _hasher) {
      require(_denomination > 0, "denomination shoule be greater than 0");
      verifier = _verifier;
      denomination = _denomination;
  }

  function deposit(bytes32 _commitment) external payable nonReentrant {
    uint32 insertedIndex = _insert(_commitment);
    _processDeposit();

    emit Deposit(_commitment, insertedIndex, block.timestamp);
  }

  function withdraw(
    Proof calldata proof,
    bytes32 _root,
    bytes32 _nullifierHash,
    address payable _recipient,
    address payable _relayer,
    uint256 _fee
    ) external payable nonReentrant {
    require(!nullifierHashes[_nullifierHash], "nullifier has spent");
    require(isKnownRoot(_root), "cannot find merkle root");
    require(verifier.verifyProof(proof.a, proof.b, proof.c, [
      uint256(_root),
      uint256(_nullifierHash),
      uint256(0x111111), // TODO eric
      uint256(0x111111), // TODO eric
      _fee
      ]), "Invalid withdraw proof");
    
    nullifierHashes[_nullifierHash] = true;
    _processWithdraw(_recipient, _relayer, _fee);
    emit Withdraw(_recipient, _nullifierHash, _relayer, _fee);
  }

  function _processDeposit() internal virtual;
  function _processWithdraw(address payable _recipient, address payable _relayer, uint256 _fee) internal virtual;

  function isSpent(bytes32 _nullifierHash) public view returns (bool) {
    return nullifierHashes[_nullifierHash];
  }

  function isSpentArray(bytes32[] calldata _nullifierHashes) external view returns (bool[] memory spent) {
    spent = new bool[](_nullifierHashes.length);
    for (uint256 i = 0; i < _nullifierHashes.length; i++) {
      if (isSpent(_nullifierHashes[i])) {
        spent[i] = true;
      }
    }
  }
}