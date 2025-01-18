// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import "../RatesBase.t.sol";
import "../../src/repositories/Rates800To1599.sol";

contract Rates800To1599Test is RatesBase {
    function createCalculator() internal override returns (RatesLike) {
        return RatesLike(address(new Rates800To1599()));
    }
}