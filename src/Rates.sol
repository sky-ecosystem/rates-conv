// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

interface RatesLike {
    function turn(uint256 bps) external view returns (uint256);
}

contract Rates {

    address[] public rates;

    constructor(address[] memory _rates) {
        rates = _rates;
    }

    function turn(uint256 bps) external view returns (uint256 rate) {
        rate = RatesLike(rates[bps / 800]).turn(bps);
    }
}