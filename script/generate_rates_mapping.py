#!/usr/bin/env python3

import requests
import re
from pathlib import Path

def fetch_ipfs_data(ipfs_url):
    response = requests.get(ipfs_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from {ipfs_url}")
    return response.text

def parse_rates(text):
    rates = {}
    pattern = r'(\d+\.\d+)%: (\d+)'
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        match = re.match(pattern, line)
        if match:
            percentage = float(match.group(1))
            value = match.group(2)
            # Convert percentage to index by multiplying by 100 and rounding
            index = round(percentage * 100)  
            rates[index] = value
    
    return rates

def generate_solidity_contract(rates):
    contract_template = '''// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity 0.8.24;

contract RatesMapping {
    mapping(uint256 => uint256) public rates;

    constructor() {
%s
    }
}'''
    
    # Generate constructor body
    constructor_lines = []
    for index, value in sorted(rates.items()):
        constructor_lines.append(f"        rates[{index}] = {value};")
    
    constructor_body = "\n".join(constructor_lines)
    return contract_template % constructor_body

def main():
    ipfs_url = "https://ipfs.io/ipfs/QmVp4mhhbwWGTfbh2BzwQB9eiBrQBKiqcPRZCaAxNUaar6"
    output_file = Path("/Users/odd/Documents/rates-repository/test/RatesMapping.sol")
    
    # Fetch and combine all chunks
    print("Fetching data from IPFS...")
    data = fetch_ipfs_data(ipfs_url)
    
    # Parse the rates
    print("Parsing rates...")
    rates = parse_rates(data)
    print(f"Found {len(rates)} rates")
    
    if len(rates) == 0:
        print("No rates found! Sample of data received:")
        print(data[:500])
        return
    
    # Generate the Solidity contract
    print("Generating Solidity contract...")
    contract = generate_solidity_contract(rates)
    
    # Write the contract to file
    print(f"Writing contract to {output_file}...")
    output_file.write_text(contract)
    print(f"Done! Generated {len(rates)} rates entries.")

if __name__ == "__main__":
    main()
