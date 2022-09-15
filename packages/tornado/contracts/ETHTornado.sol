// SPDX-License-Identifier: GPL-3.0-only

pragma solidity 0.8.9;

import "./Tornado.sol";

contract ETHTornado is Tornado {
  constructor(
    IVerifier _verifier, 
    uint256 _denomination, 
    uint32 _merkleTreeHeight, 
    address _hasher) Tornado(_verifier, _denomination, _merkleTreeHeight, _hasher) {}
  
  function _processDeposit() internal override {
    require(msg.value == denomination, "Please send denomination ETH within tx");
  }

  function _processWithdraw(address payable _recipient, address payable _relayer, uint256 _fee) internal override {
    require(msg.value == 0, "Message value is suposed to be zero");
    (bool success, ) = _recipient.call{value: (denomination - _fee)}("");
    require(success, "Payment to recipient failed");
    if (_fee > 0) {
      (success, ) = _relayer.call{value: _fee}("");
      require(success, "payment to relayer failed");
    }
  }
}