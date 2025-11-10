### Problem Statement

Tyger has an array of `n` values, where each integer between 1 and `n`, inclusive, occurs exactly once. Regyt is unpleased with the arrangement of values, and provides instructions for Tyger to rearrange his array.

Regyt's instructions come in the form of `q` queries. Each query requires Tyger to swap the positions of two values, `x` and `y`, in the array. `x` and `y` refer to values, not indices. To check his work, Tyger would like you to determine the final array!

### Additional Notes
**Time Limit:**
*   C++: 2.5 seconds
*   Java, Python: 5 seconds

**Memory Limit:** 128MB

### Input Format
The first line contains a single integer `n` (1 ≤ `n` ≤ 10<sup>5</sup>), representing the size of the permutation.

The second line contains `n` integers, representing the array `p`<sub>1</sub>, ..., `p`<sub>n</sub>.

The next line contains a single integer `q` (1 ≤ `q` ≤ 10<sup>5</sup>), representing the number of queries.

Then, `q` lines follow. Each line contains two integers `x` and `y` (1 ≤ `x`, `y` ≤ `n`), representing the values to swap.

### Output Format
Output `n` integers, the resulting array after performing all the swaps.

### Scoring
In tests worth 50 points, it is guaranteed that 1 ≤ `n`, `q` ≤ 1000.

### Sample Input
```
7
5 2 3 7 4 1 6
4
1 2
6 7
2 5
3 5
```

### Sample Output
```
2 1 5 6 4 3 7
```

### Sample Explanation
After each instruction, the array becomes:

1.  Initial array: `5 2 3 7 4 1 6`
2.  Swap 1 and 2: `5 1 3 7 4 2 6`
3.  Swap 6 and 7: `5 1 3 6 4 2 7`
4.  Swap 2 and 5: `2 1 3 6 4 5 7`
5.  Swap 3 and 5: `2 1 5 6 4 3 7`