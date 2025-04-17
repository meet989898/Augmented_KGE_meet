import numpy as np
import pandas as pd
import time

# Generate test data
small_set1 = np.random.randint(0, 1000, size=5000)
small_set2 = np.random.randint(0, 1000, size=5000)

large_set1 = np.random.randint(0, 1_000_000, size=500_000_000)
large_set2 = np.random.randint(0, 1_000_000, size=500_000_000)

# Convert to Python sets
small_py_set1 = set(small_set1)
small_py_set2 = set(small_set2)

large_py_set1 = set(large_set1)
large_py_set2 = set(large_set2)

# Benchmark NumPy for small sets
start = time.time()
np.union1d(small_set1, small_set2)
np_time_small_union = time.time() - start

start = time.time()
np.intersect1d(small_set1, small_set2)
np_time_small_intersect = time.time() - start

# Benchmark Python sets for small sets
start = time.time()
small_py_set1.union(small_py_set2)
py_time_small_union = time.time() - start

start = time.time()
small_py_set1.intersection(small_py_set2)
py_time_small_intersect = time.time() - start

# Benchmark NumPy for large sets
start = time.time()
np.union1d(large_set1, large_set2)
np_time_large_union = time.time() - start

start = time.time()
np.intersect1d(large_set1, large_set2)
np_time_large_intersect = time.time() - start

# Benchmark Python sets for large sets
start = time.time()
large_py_set1.union(large_py_set2)
py_time_large_union = time.time() - start

start = time.time()
large_py_set1.intersection(large_py_set2)
py_time_large_intersect = time.time() - start

# Create results

df = pd.DataFrame({
    "Operation": ["Union (Small)", "Intersection (Small)", "Union (Large)", "Intersection (Large)"],
    "NumPy Time (s)": [np_time_small_union, np_time_small_intersect, np_time_large_union, np_time_large_intersect],
    "Python Set Time (s)": [py_time_small_union, py_time_small_intersect, py_time_large_union, py_time_large_intersect]
})


print(df)
