// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IOracleU} from "./IOracleU.sol";

// Malicious oracle that returns a value where:
// - Lower 128 bits are <= MAX_BONUS (passes the uint128 cast check)
// - Full 256-bit value is much larger than MAX_BONUS
contract MaliciousOracle is IOracleU {
    function adjust(address) external pure override returns (uint256) {
        // 2^128 + 1
        // uint128(this) = 1, which is <= 100 ether
        // But the full value is 2^128 + 1, which is >> 100 ether
        return (uint256(1) << 128) + 1;
    }
}
