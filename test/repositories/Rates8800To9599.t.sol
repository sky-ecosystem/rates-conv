// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import "../RatesBase.t.sol";
import "../../src/repositories/Rates8800To9599.sol";

contract Rates8800To9599Test is RatesBase {
    function createCalculator() internal override returns (RatesLike) {
        return RatesLike(address(new Rates8800To9599()));
    }
}