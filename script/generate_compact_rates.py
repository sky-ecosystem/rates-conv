#!/usr/bin/env python3

import struct

def int_to_bytes8(n: int) -> str:
    """Convert integer to 8-byte hex string in big-endian format for Solidity."""
    # Convert to hex, remove '0x' prefix, pad to 16 chars (8 bytes)
    return format(n & ((1 << 64) - 1), '016x')

def parse_rates_mapping(file_path, max_bps=5000):
    """Parse rates from RatesMapping.sol up to max_bps."""
    rates = {}
    with open(file_path, 'r') as f:
        for line in f:
            if 'rates[' in line and '] =' in line:
                parts = line.strip().split('rates[')[1].split('] =')
                bps = int(parts[0])
                if bps <= max_bps:  # Only include rates up to max_bps
                    rate = int(parts[1].strip().rstrip(';'))
                    rates[bps] = rate
    return rates

def pack_rates(rates):
    packed = bytearray()
    for rate in rates:
        # Pack each rate as a full 8-byte value
        packed.extend(rate.to_bytes(8, 'big'))
    return bytes(packed)

def generate_contract() -> str:
    """Generate compact bytes representation and contract for all rates in RatesMapping.sol."""
    RAY = 10**27
    all_bytes = []
    
    # Get rates from RatesMapping.sol
    rates = parse_rates_mapping('src/mock/RatesMapping.sol')
    
    # Sort rates by bps to ensure correct order
    sorted_bps = sorted(rates.keys())
    start_bps = sorted_bps[0]
    end_bps = sorted_bps[-1]
    
    # Generate rates based on the mapping, ensuring 4 rates per word
    for i in range(0, len(sorted_bps), 4):
        word_rates = []
        # Get next 4 rates (or pad with zeros if at the end)
        for j in range(4):
            if i + j < len(sorted_bps):
                bps = sorted_bps[i + j]
                rate = rates[bps]
                # Store rate - RAY, ensure it fits in uint64
                adjusted_rate = rate - RAY
                if adjusted_rate >= (1 << 64):
                    raise ValueError(f"Rate difference too large for bps {bps}: {adjusted_rate}")
                hex_rate = int_to_bytes8(adjusted_rate)
            else:
                # Pad with zeros if we don't have enough rates
                hex_rate = '0' * 16
            word_rates.append(hex_rate)
        all_bytes.extend(word_rates)
    
    # Join all bytes into one big hex string without length prefix
    compact_bytes = f'hex"{"".join(all_bytes)}"'
    
    # Create the contract
    contract_template = f'''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract Conv {{
    uint256 constant public MAX = {end_bps};
    uint256 constant internal RAY = 10**27;
    
    // Each rate takes 8 bytes (64 bits), total of {len(sorted_bps)} rates
    // Each storage word (32 bytes) contains exactly 4 rates
    // Total size = {len(sorted_bps)} * 8 = {len(sorted_bps) * 8} bytes
    bytes internal RATES;

    constructor() {{
        RATES = {compact_bytes};
    }}

    /// @notice Fetches the rate for a given basis points value
    /// @param bps The basis points value to get the rate for
    /// @return rate The annual rate value
    function turn(uint256 bps) public view returns (uint256 rate) {{
        require(bps <= MAX);
        
        assembly {{
            let offset := mul(bps, 8)       // Each rate is 8 bytes
            let wordPos := div(offset, 32)  // Which 32-byte word to read
            let bytePos := mod(offset, 32)  // Position within the word

            let dataSlot := keccak256(RATES.slot, 0x20)
            
            let value := sload(add(dataSlot, wordPos))
            
            let shifted := shr(mul(sub(24, bytePos), 8), value)
            
            rate := add(and(shifted, 0xFFFFFFFFFFFFFFFF), RAY)
        }}
    }}
}}'''
    return contract_template

def main():
    """Generate and write the contract."""
    contract = generate_contract()
    print(contract)

if __name__ == '__main__':
    main()
