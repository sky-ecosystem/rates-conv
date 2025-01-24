## Conv

**Onchain repository for DSS rates**

Conv stores all per-second DSS rates for annualized BPSs in a single on-chain repository.

### Motivation

Some parts of the DSS protocol may need rate validation, such as the rate validation of the IAM module. This repository aims to implement that.

Requirements:
- The rates need to have full precision compared to rates currently used in DSS (https://ipfs.io/ipfs/QmVp4mhhbwWGTfbh2BzwQB9eiBrQBKiqcPRZCaAxNUaar6)
- Read cost should be reasonable, allowing other components of the system to use it without too much overhead.
- The contract needs to be deployable efficiently (low priority, one time cost).

### Design

We explored several ways to store or calculate rates onchain. There are tradeoffs between different approaches as expected:

| Design   | Deployment Cost | Contract Size | Precision | Read Cost | Note |
| -------- | --------------- | ------------- | --------- | --------- | ---- |
| Plain mapping | 20M gas / 1k rates | Small | Full | 2k gas |
| Calculating onchain (ABDK lib) | low | Small | Lossy (though close) | 20k gas | External lib also used, not usually accepted for DSS modules |
| Hardcoded (script generated binary search in Solidity Assembly) | 7M gas / 1k rates | Large (fits up to 800 rates per contract) | Full | 3k gas |
| **Optimized storage** (this) | 5.6M / 1k rates | Large (fits up to 5k rates on Ethereum mainnet, rates are hardcoded on the constructor) | Full | 3k gas

Optimized storage was the choice as it represents the best tradeoffs between all the approaches.

### How it works

The contract makes use of optimized storage to ease the cost of deployment. Each rate is stored as `rate - RAY`, so only the relevant part of the rate takes space in storage. Each rate is stored in 8 bytes, so every storage position fits exactly four rates.

On reads, the function `turn(bps)` will fetch the correct storage slot, fetch the desired rate within it, add one RAY and return the result

### Limitations

- Since rates are stored in 8 bytes, the max BPS that can be used without reimplementing this contract is **7891**.
- EIP-170: Due to contract size limits on Ethereum mainnet, the ceiling for rates is 6k. On L2s that do not enforce the limit this does not apply.
- Gas cost of deployment: With the current 30M block gas ceiling on Ethereum mainnet, up to ~5.5k rates can be stored.

## Deployments

- **5000bps Ethereum Mainnet**: tbd

## Usage

### Build

```shell
$ forge build
```

### Test

```shell
$ forge test
```

### Gas Snapshots

```shell
$ forge snapshot
```

### Deploy

```shell
$ forge create Conv --broadcast
```