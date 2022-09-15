// SPDX-License-Identifier: GPL-3.0-only

pragma solidity 0.8.9;

interface Hasher {
  function poseidon(bytes32[2] calldata leftRightLeaf) 
    external 
    pure 
    returns (bytes32);
}

contract MerkleTreeWithHistory {
  uint256 public constant FIELD_SIZE = 21888242871839275222246405745257275088548364400416034343698204186575808495617;
  uint256 public constant ZERO_VALUE = 21663839004416932945382355908790599225266501822907911457504978515578255421292;

  Hasher public hasher;

  uint32 public immutable levels;

  bytes32[] public filledSubtrees;
  bytes32[] public zeros;
  
  uint32 public currentRootIndex = 0;
  uint32 public nextIndex = 0;
  uint32 public constant ROOT_HISTORY_SIZE = 100;
  bytes32[ROOT_HISTORY_SIZE] public roots;

  constructor(uint32 _treeLevels, address _hasher) {
    require(_treeLevels > 0, "_treeLevels should be greater than zero");
    require(_treeLevels < 32, "_treeLevels should be less than 32");

    hasher = Hasher(_hasher);
    levels = _treeLevels;

    bytes32 currentZero = bytes32(ZERO_VALUE);
    zeros.push(currentZero);
    filledSubtrees.push(currentZero);

    for (uint32 i = 1; i < _treeLevels; i++) {
      currentZero = hashLeftRight(currentZero, currentZero);
      zeros.push(currentZero);
      filledSubtrees.push(currentZero);
    }

    roots[0] = hashLeftRight(currentZero, currentZero);
  }

  function hashLeftRight(bytes32 left, bytes32 right) public view returns (bytes32) {
    require(uint256(left) < FIELD_SIZE, "left should be inside the field");
    require(uint256(right) < FIELD_SIZE, "right should be inside the field");

    bytes32[2] memory leftRight = [left, right];
    return hasher.poseidon(leftRight);
  }

  function _insert(bytes32 _leaf) internal returns (uint32 index) {
    uint32 currentIndex = nextIndex;
    require(currentIndex != uint32(2)**levels, "Merkle tree is full, No more leafs can be added");
    nextIndex += 1;
    bytes32 currentLevelHash = _leaf;
    bytes32 left;
    bytes32 right;

    for (uint32 i = 0; i < levels; i++) {
      if (currentIndex % 2 == 0) {
        left = currentLevelHash;
        right = zeros[i];

        filledSubtrees[i] = currentLevelHash;
      } else {
        left = filledSubtrees[i];
        right = currentLevelHash;
      }

      currentLevelHash = hashLeftRight(left, right);
      currentIndex /= 2;
    }

    currentRootIndex = (currentRootIndex + 1) % ROOT_HISTORY_SIZE;
    roots[currentRootIndex] = currentLevelHash;
    return nextIndex - 1;
  }

  function isKnownRoot(bytes32 root) public view returns (bool) {
    if (root == 0) return false;

    uint32 i = currentRootIndex;
    do {
      if (root == roots[i]) return true;
      if (i == 0) i = ROOT_HISTORY_SIZE;
      i--;
    } while (i != currentRootIndex);
    return false;
  }

  function getLastRoot() public view returns (bytes32) {
    return roots[currentRootIndex];
  }
}