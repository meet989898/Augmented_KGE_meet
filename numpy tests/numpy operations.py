import numpy as np

# Sample sets
set1 = np.array([1, 2, 3, 4, 5])
set2 = np.array([4, 5, 6, 7, 8])

# Union
union_result = np.union1d(set1, set2)
print("Union:", union_result)

# Intersection
intersection_result = np.intersect1d(set1, set2)
print("Intersection:", intersection_result)
