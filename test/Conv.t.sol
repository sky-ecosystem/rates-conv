// SPDX-FileCopyrightText: © 2025 Dai Foundation <www.daifoundation.org>
// SPDX-License-Identifier: AGPL-3.0-or-later
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

pragma solidity 0.8.19;

import "forge-std/Test.sol";
import "../src/conv.sol";
import "./RatesMapping.sol";

contract ConvTest is Test {
    Conv public conv;
    RatesMapping public ratesMapping;
    uint256 public maxBps;

    function setUp() public {
        conv = new Conv();
        ratesMapping = new RatesMapping();
        maxBps = conv.MAX();
    }

    function testCompareAllRates() public view {
        for (uint256 bps = 0; bps <= maxBps; bps++) {
            uint256 mappingRate = ratesMapping.rates(bps);
            uint256 bytesRate = conv.turn(bps);

            assertEq(bytesRate, mappingRate, string.concat("Rate mismatch at bps=", vm.toString(bps)));
        }
    }

    function testRevertsForInvalidBps() public {
        vm.expectRevert();
        conv.turn(maxBps + 1);

        vm.expectRevert();
        conv.turn(maxBps + 100);

        vm.expectRevert();
        conv.turn(1000 ether);
    }

    function testGas() public {
        uint256 gasBefore = gasleft();
        new Conv();
        console.log("Deploy: ", gasBefore - gasleft());

        for (uint256 i; i <= maxBps; i += 123) {
            gasBefore = gasleft();
            conv.turn(i);
            console.log("Turn bps", i, ":", gasBefore - gasleft());
        }
    }

    function testFuzz(uint256 bps) public view {
        try conv.turn(bps) returns (uint256 result) {
            assertTrue(bps <= maxBps);
            assertEq(result, ratesMapping.rates(bps));
        } catch {
            assertTrue(bps > maxBps);
        }
    }
}
