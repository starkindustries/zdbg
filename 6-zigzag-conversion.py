

class Solution:
    def convert(self, s: str, numRows: int) -> str:
        conversion = [""] * numRows
        print(conversion)
        idx = 0
        # Ex: numRows 4: 0 1 2 3 2 1 repeat
        idx_sequence = list(range(numRows)) + list(range(numRows-2, 0, -1))
        while idx < len(s):
            for j in idx_sequence:
                conversion[j] += s[idx]
                idx += 1
                if idx >= len(s):
                    break
        return "".join(conversion)

s = "6_LEETCODE_ZIGZAG_CONVERSION"
solve = Solution()
result = solve.convert(s, 4)
print(result)
