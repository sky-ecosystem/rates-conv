// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import "../RatesBase.t.sol";
import "../../src/repositories/Rates6400To7199.sol";

contract Rates6400To7199Test is RatesBase {
    function createCalculator() internal override returns (RatesLike) {
        return RatesLike(address(new Rates6400To7199()));
    }
}