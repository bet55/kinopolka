class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        left = 0
        max_len = 1

        for i, c in enumerate(s):
            window = s[left : i + 1]

            if len(set(window)) == len(window):
                max_len = max(max_len, i - left + 1)
            else:
                left += 1
        return max_len
