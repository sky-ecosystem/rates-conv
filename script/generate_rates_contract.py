#!/usr/bin/env python3

import sys
from typing import Dict, List
import os

def extract_rates_from_mapping(solidity_file: str, start_bps: int, end_bps: int) -> Dict[int, str]:
    """Extract the rates mapping from the RatesMapping contract within the specified range."""
    rates = {}
    with open(solidity_file, 'r') as f:
        for line in f:
            if 'rates[' in line and '] =' in line:
                parts = line.strip().split('=')
                bps = int(parts[0].split('[')[1].split(']')[0])
                if start_bps <= bps <= end_bps:
                    rate = parts[1].strip().rstrip(';')
                    rates[bps] = rate
    return rates

def generate_switch_block(rates: Dict[int, str], start: int, end: int, indent: str = "") -> str:
    """Generate a binary search switch block for a range of rates."""
    if end - start <= 25:  # Base case: generate direct switch for small ranges
        cases = []
        cases.append(f"{indent}switch bps")
        for bps in range(start, end + 1):
            if bps in rates:
                cases.append(f"{indent}    case {bps} {{ rate := {rates[bps]} }}")
        cases.append(f"{indent}    default {{ revert(0, 0) }}")
        return "\n".join(cases)
    
    mid = (start + end) // 2
    return f"""{indent}switch gt(bps, {mid})
{indent}    case 0 {{ // {start}-{mid}
{generate_switch_block(rates, start, mid, indent + "        ")}
{indent}    }}
{indent}    case 1 {{ // {mid+1}-{end}
{generate_switch_block(rates, mid + 1, end, indent + "        ")}
{indent}    }}
{indent}    default {{ revert(0, 0) }}"""

def ensure_directory_exists(filepath: str):
    """Ensure the directory for the given file path exists."""
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)

def generate_test_file(output_file: str, contract_name: str):
    """Generate the test file for the contract."""
    ensure_directory_exists(output_file)
    test = f"""// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import "../RatesBase.t.sol";
import "../../src/repositories/{contract_name}.sol";

contract {contract_name}Test is RatesBase {{
    function createCalculator() internal override returns (RatesLike) {{
        return RatesLike(address(new {contract_name}()));
    }}
}}"""

    with open(output_file, 'w') as f:
        f.write(test)

def generate_contract(input_file: str, contract_name: str = "Rates", start_bps: int = 0, end_bps: int = 800):
    """Generate the optimized Rates contract for a specific range."""
    # Determine output paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(script_dir)
    contract_file = os.path.join(repo_dir, "src", "repositories", f"{contract_name}.sol")
    test_file = os.path.join(repo_dir, "test", "repositories", f"{contract_name}.t.sol")

    rates = extract_rates_from_mapping(input_file, start_bps, end_bps)
    if not rates:
        print(f"No rates found in input file for range {start_bps}-{end_bps}")
        return

    contract = f"""// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

contract {contract_name} {{
    uint256 constant public MIN = {start_bps};
    uint256 constant public MAX = {end_bps};

    function turn(uint256 bps) external pure returns (uint256 rate) {{
        if (bps > MAX) revert();
        if (bps < MIN) revert();
        
        assembly {{
{generate_switch_block(rates, start_bps, end_bps, "            ")}
        }}
    }}
}}"""

    # Generate the contract file
    ensure_directory_exists(contract_file)
    with open(contract_file, 'w') as f:
        f.write(contract)
    print(f"Generated contract file: {contract_file}")

    # Generate the test file
    generate_test_file(test_file, contract_name)
    print(f"Generated test file: {test_file}")

def generate_all_contracts(input_file: str, step: int = 800, max_bps: int = 10000):
    """Generate contracts for all ranges up to max_bps in given step increments."""
    start = 0
    while start < max_bps:
        end = min(start + step - 1, max_bps)  # -1 because each range should not overlap
        contract_name = f"Rates{start}To{end}"
        print(f"\nGenerating contract for range {start}-{end}...")
        generate_contract(input_file, contract_name, start, end)
        start += step

if __name__ == "__main__":
    if len(sys.argv) == 2:
        # If only input file is provided, generate all contracts
        input_file = sys.argv[1]
        generate_all_contracts(input_file)
    elif len(sys.argv) == 5:
        # If all arguments are provided, generate single contract
        input_file = sys.argv[1]
        start_bps = int(sys.argv[2])
        end_bps = int(sys.argv[3])
        contract_name = sys.argv[4]
        generate_contract(input_file, contract_name, start_bps, end_bps)
    else:
        print("Usage:")
        print("  To generate all contracts:")
        print("    python generate_rates_contract.py <input_solidity_file>")
        print("  To generate a single contract:")
        print("    python generate_rates_contract.py <input_solidity_file> <start_bps> <end_bps> <contract_name>")
        sys.exit(1)
