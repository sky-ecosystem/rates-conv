// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import "forge-std/Test.sol";
import "../src/Rates.sol";
import "./RatesMapping.sol";
import "../src/repositories/Rates0To799.sol";
import "../src/repositories/Rates800To1599.sol";
import "../src/repositories/Rates1600To2399.sol";
import "../src/repositories/Rates2400To3199.sol";
import "../src/repositories/Rates3200To3999.sol";
import "../src/repositories/Rates4000To4799.sol";
import "../src/repositories/Rates4800To5599.sol";
import "../src/repositories/Rates5600To6399.sol";
import "../src/repositories/Rates6400To7199.sol";
import "../src/repositories/Rates7200To7999.sol";
import "../src/repositories/Rates8000To8799.sol";
import "../src/repositories/Rates8800To9599.sol";
import "../src/repositories/Rates9600To10000.sol";

contract RatesTest is Test {
    Rates rates;
    RatesMapping referenceRates;
    address[] rateAddresses;

    function setUp() public {
        referenceRates = new RatesMapping();

        rateAddresses = new address[](13);
        rateAddresses[0] = address(new Rates0To799());
        rateAddresses[1] = address(new Rates800To1599());
        rateAddresses[2] = address(new Rates1600To2399());
        rateAddresses[3] = address(new Rates2400To3199());
        rateAddresses[4] = address(new Rates3200To3999());
        rateAddresses[5] = address(new Rates4000To4799());
        rateAddresses[6] = address(new Rates4800To5599());
        rateAddresses[7] = address(new Rates5600To6399());
        rateAddresses[8] = address(new Rates6400To7199());
        rateAddresses[9] = address(new Rates7200To7999());
        rateAddresses[10] = address(new Rates8000To8799());
        rateAddresses[11] = address(new Rates8800To9599());
        rateAddresses[12] = address(new Rates9600To10000());

        rates = new Rates(rateAddresses);
    }

    function testAllRates() public view {
        for (uint256 bps = 0; bps <= 10000; bps++) {
            uint256 rate = rates.turn(bps);
            uint256 expectedRate = referenceRates.rates(bps);
            
            assertEq(
                rate, 
                expectedRate, 
                string(abi.encodePacked("Rate mismatch for bps: ", vm.toString(bps)))
            );
        }
    }

    function testRevertOnTooHighBps() public {
        vm.expectRevert();
        rates.turn(10001);
    }
}
