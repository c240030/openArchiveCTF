### Problem Statement

Tyger has a bunch of blocks that form a 2-dimensional connected shape on a square grid. He wants to rotate the shape clockwise by 90 degrees, and can only do so by moving some of the blocks around. Note that you can move blocks out of the original `n x n` grid. Please help him calculate the minimum number of blocks he needs to move to successfully rotate the shape!

### Additional Notes
**Time Limit:**
*   C++: 2.5 seconds
*   Java, Python: 5 seconds

**Memory Limit:** 128MB

### Input Format
The first line contains a single integer `t` (1 ≤ `t` ≤ 5), the number of testcases.

The first line of each testcase contains a single integer `n` (1 ≤ `n` ≤ 50), denoting the number of rows and columns of the grid.

Then, `n` lines follow, each containing `n` characters. The character in the `i`-th row and the `j`-th column is '1' if the corresponding cell contains a block, and '0' otherwise.

### Output Format
For each testcase, output a single integer, the minimum number of blocks Tyger needs to move to rotate the shape clockwise by 90 degrees.

### Sample Input
```
2
3
100
100
111
4
1111
1010
1010
1010
```

### Sample Output
```
2
3
```

### Sample Explanation
In the second testcase, you can move the block at (1, 4) to (1, 0), the one at (4, 1) to (3, 0), and the block at (2, 1) to (3, 2). It can be proven that it's impossible to rotate the shape by moving less than 3 blocks.