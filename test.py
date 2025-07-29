# Definition for a binary tree node.
class TreeNode(object):
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
        
from collections import deque

class Solution(object):
    def averageOfLevels(self, root):
        """
        :type root: Optional[TreeNode]
        :rtype: List[float]
        """
        # bfs traversal 
        q = deque()
        result = []
        q.append(root)
        while q:
            level = []
            size = len(q)
            for i in range(size):
                current = q.popleft()
                level.append(current.val)
                if current.left:
                    q.append(current.left)
                if current.right:
                    q.append(current.right)
            print(level)
            result.append(sum(level)/size)
        return result
            

        
            
        
            
if __name__ == "__main__":
    sol = Solution()
    print(sol.averageOfLevels([3,9,20,15,7]))
    print(sol.averageOfLevels([3,9,20,15,7]))
    