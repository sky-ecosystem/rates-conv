// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import "../RatesBase.t.sol";
import "../../src/repositories/Rates4000To4799.sol";

contract Rates4000To4799Test is RatesBase {
    function createCalculator() internal override returns (RatesLike) {
        return RatesLike(address(new Rates4000To4799()));
    }
}