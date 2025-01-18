// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import "forge-std/Test.sol";
import "./RatesMapping.sol";

interface RatesLike {
    function MIN() external view returns (uint256);
    function MAX() external view returns (uint256);
    function turn(uint256 bps) external view returns (uint256);
}

abstract contract RatesBase is Test {
    RatesLike public calculator;
    RatesMapping public ratesMapping;
    
    uint256 constant RAY = 1e27;
    uint256 public immutable MIN;
    uint256 public immutable MAX;
    
    constructor() {
        calculator = createCalculator();
        ratesMapping = new RatesMapping();
        MIN = calculator.MIN();
        MAX = calculator.MAX();
    }
    
    function testAllValues() public view {
        for (uint256 bps = MIN; bps <= MAX; bps += 1) {
            uint256 mappingRate = ratesMapping.rates(bps);
            uint256 calculatedRate = calculator.turn(bps);
            assertEq(
                calculatedRate,
                mappingRate,
                string.concat("Rate mismatch for ", vm.toString(bps), " basis points")
            );
        }
    }
    
    function testInvalidInputs() public {
        if (MIN > 0) {
            vm.expectRevert();
            calculator.turn(MIN - 1);
        }

        if (MIN > 10) {
            vm.expectRevert();
            calculator.turn(MIN - 10);
        }
        
        vm.expectRevert();
        calculator.turn(MAX + 1);
        
        vm.expectRevert();
        calculator.turn(MAX + 1000);
    }

    function testGasCosts() public {
        // Measure deployment cost
        uint256 gasBefore = gasleft();
        calculator = createCalculator();
        uint256 gasAfter = gasleft();
        uint256 deploymentGas = gasBefore - gasAfter;
        console.log("Deployment gas cost:", deploymentGas);

        uint256 max;
        uint256 min;
        uint256 total;

        for (uint256 i = MIN; i <= MAX; i++) {
            gasBefore = gasleft();
            calculator.turn(i);
            gasAfter = gasleft();

            uint256 gasSpent = gasBefore - gasAfter;
            total += gasSpent;
            if (gasSpent > max) max = gasSpent;
            if (gasSpent < min || min == 0) min = gasSpent;
        }

        console.log("Max gas spent:", max);
        console.log("Min gas spent:", min);
        console.log("Average gas spent:", total / (MAX - MIN + 1));
    }

    function createCalculator() internal virtual returns (RatesLike);
}
