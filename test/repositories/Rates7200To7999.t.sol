// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import "../RatesBase.t.sol";
import "../../src/repositories/Rates7200To7999.sol";

contract Rates7200To7999Test is RatesBase {
    function createCalculator() internal override returns (RatesLike) {
        return RatesLike(address(new Rates7200To7999()));
    }
}